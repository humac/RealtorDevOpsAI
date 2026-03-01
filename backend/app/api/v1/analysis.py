"""Property analysis endpoint - orchestrates data collection and AI analysis."""

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.property import Property
from app.models.scenario import DevelopmentScenario
from app.schemas.property import AnalyzePropertyRequest
from app.schemas.scenario import AnalysisResponse
from app.services.ai_analysis import build_analysis_response, generate_scenarios
from app.services.data_aggregator import aggregate_property_data
from app.services.zoning_parser import (
    calculate_development_potential,
    get_zoning_envelope,
)

router = APIRouter()


@router.post("", response_model=AnalysisResponse)
async def analyze_property(
    request: AnalyzePropertyRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Analyze a property for development potential.

    Orchestrates data collection from Ottawa Open Data, GeoOttawa,
    zoning by-law parsing, AI scenario generation, and cost estimation.
    """
    # 1. Try to find existing property in DB
    existing_property = None
    if request.parcel_id:
        result = await db.execute(
            select(Property).where(Property.parcel_id == request.parcel_id)
        )
        existing_property = result.scalar_one_or_none()
    elif request.address:
        result = await db.execute(
            select(Property).where(Property.address.ilike(f"%{request.address}%"))
        )
        existing_property = result.scalar_one_or_none()

    # 2. Aggregate data from external sources if not in DB
    if existing_property:
        property_data = {
            "id": str(existing_property.id),
            "parcel_id": existing_property.parcel_id,
            "address": existing_property.address,
            "lot_width_ft": existing_property.lot_width_ft,
            "lot_depth_ft": existing_property.lot_depth_ft,
            "lot_area_sqft": existing_property.lot_area_sqft,
            "current_use": existing_property.current_use,
            "structure_type": existing_property.structure_type,
            "year_built": existing_property.year_built,
            "gross_floor_area_sqft": existing_property.gross_floor_area_sqft,
            "assessed_value": existing_property.assessed_value,
            "assessed_land_value": existing_property.assessed_land_value,
            "zoning_code": existing_property.zoning_code,
            "ward": existing_property.ward,
            "neighbourhood": existing_property.neighbourhood,
            "is_heritage": existing_property.is_heritage,
            "is_floodplain": existing_property.is_floodplain,
            "has_easements": existing_property.has_easements,
            "environmental_constraints": existing_property.environmental_constraints,
        }
    else:
        property_data = await aggregate_property_data(
            address=request.address,
            parcel_id=request.parcel_id,
        )

        if not property_data:
            # Create a minimal property record for analysis with provided data
            property_data = {
                "id": str(uuid.uuid4()),
                "parcel_id": request.parcel_id or "unknown",
                "address": request.address or "Unknown",
                "lot_width_ft": None,
                "lot_depth_ft": None,
                "lot_area_sqft": None,
                "current_use": "unknown",
                "structure_type": "unknown",
                "year_built": None,
                "gross_floor_area_sqft": None,
                "assessed_value": request.acquisition_cost,
                "zoning_code": None,
                "is_heritage": False,
                "is_floodplain": False,
                "has_easements": False,
            }

    # Add request params to property data
    property_data["acquisition_cost"] = request.acquisition_cost or property_data.get("assessed_value", 0)
    property_data["target_use"] = request.target_use

    # 3. Parse zoning
    zoning_code = property_data.get("zoning_code")
    zoning_envelope = get_zoning_envelope(zoning_code) if zoning_code else None

    # 4. Calculate development potential
    dev_potential = {}
    if zoning_envelope and property_data.get("lot_area_sqft"):
        dev_potential = calculate_development_potential(
            zoning_envelope,
            lot_area_sqft=property_data["lot_area_sqft"],
            lot_width_ft=property_data.get("lot_width_ft"),
            lot_depth_ft=property_data.get("lot_depth_ft"),
        )

    # 5. Generate AI scenarios
    ai_result = await generate_scenarios(property_data, zoning_envelope, dev_potential)

    # 6. Build response
    response = build_analysis_response(property_data, zoning_envelope, dev_potential, ai_result)
    response["generated_at"] = datetime.now(timezone.utc).isoformat()

    # 7. Store scenarios in DB
    if existing_property:
        for s in response.get("scenarios", []):
            scenario = DevelopmentScenario(
                property_id=existing_property.id,
                scenario_type=s["scenario_type"],
                title=s["title"],
                description=s["description"],
                target_use=s["target_use"],
                proposed_units=s.get("proposed_units"),
                proposed_storeys=s.get("proposed_storeys"),
                proposed_gfa_sqft=s.get("proposed_gfa_sqft"),
                total_cost=s["costs"]["total"],
                cost_breakdown=s["costs"],
                projected_sale_revenue=s.get("projected_sale_revenue"),
                projected_annual_rental=s.get("projected_annual_rental"),
                profit=s["roi_metrics"]["profit"],
                roi_pct=s["roi_metrics"]["roi_pct"],
                irr_pct=s["roi_metrics"].get("irr_pct"),
                cap_rate_pct=s["roi_metrics"].get("cap_rate_pct"),
                cash_on_cash_pct=s["roi_metrics"].get("cash_on_cash_pct"),
                timeline_months=s.get("timeline_months"),
                risks={"items": s.get("risks", [])},
                opportunity_score=s.get("opportunity_score"),
                confidence_level=s.get("confidence_level"),
                sensitivity_analysis=s.get("sensitivity_analysis"),
                ai_model_used=ai_result.get("ai_model"),
                ai_prompt_hash=ai_result.get("prompt_hash"),
            )
            db.add(scenario)

    return response
