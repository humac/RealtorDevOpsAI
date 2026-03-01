"""Scenario comparison and management endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.scenario import DevelopmentScenario

router = APIRouter()


@router.get("/property/{property_id}")
async def get_property_scenarios(
    property_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get all development scenarios for a property."""
    result = await db.execute(
        select(DevelopmentScenario)
        .where(DevelopmentScenario.property_id == property_id)
        .order_by(DevelopmentScenario.opportunity_score.desc())
    )
    scenarios = result.scalars().all()

    return [
        {
            "id": str(s.id),
            "scenario_type": s.scenario_type,
            "title": s.title,
            "description": s.description,
            "target_use": s.target_use,
            "proposed_units": s.proposed_units,
            "proposed_storeys": s.proposed_storeys,
            "proposed_gfa_sqft": s.proposed_gfa_sqft,
            "total_cost": s.total_cost,
            "roi_pct": s.roi_pct,
            "profit": s.profit,
            "timeline_months": s.timeline_months,
            "opportunity_score": s.opportunity_score,
            "confidence_level": s.confidence_level,
            "is_preferred": s.is_preferred,
            "created_at": s.created_at.isoformat() if s.created_at else None,
        }
        for s in scenarios
    ]


@router.get("/{scenario_id}")
async def get_scenario_detail(
    scenario_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get detailed scenario with full cost breakdown and sensitivity analysis."""
    result = await db.execute(
        select(DevelopmentScenario).where(DevelopmentScenario.id == scenario_id)
    )
    scenario = result.scalar_one_or_none()
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    return {
        "id": str(scenario.id),
        "property_id": str(scenario.property_id),
        "scenario_type": scenario.scenario_type,
        "title": scenario.title,
        "description": scenario.description,
        "target_use": scenario.target_use,
        "proposed_units": scenario.proposed_units,
        "proposed_storeys": scenario.proposed_storeys,
        "proposed_gfa_sqft": scenario.proposed_gfa_sqft,
        "costs": scenario.cost_breakdown,
        "total_cost": scenario.total_cost,
        "projected_sale_revenue": scenario.projected_sale_revenue,
        "projected_annual_rental": scenario.projected_annual_rental,
        "roi_metrics": {
            "profit": scenario.profit,
            "profit_margin_pct": scenario.profit_margin_pct,
            "roi_pct": scenario.roi_pct,
            "irr_pct": scenario.irr_pct,
            "cap_rate_pct": scenario.cap_rate_pct,
            "cash_on_cash_pct": scenario.cash_on_cash_pct,
        },
        "timeline_months": scenario.timeline_months,
        "risks": scenario.risks,
        "opportunity_score": scenario.opportunity_score,
        "confidence_level": scenario.confidence_level,
        "sensitivity_analysis": scenario.sensitivity_analysis,
        "is_preferred": scenario.is_preferred,
        "ai_model_used": scenario.ai_model_used,
        "created_at": scenario.created_at.isoformat() if scenario.created_at else None,
    }


@router.post("/compare")
async def compare_scenarios(
    scenario_ids: list[UUID] = Query(..., description="Scenario IDs to compare"),
    db: AsyncSession = Depends(get_db),
):
    """Compare multiple scenarios side-by-side."""
    result = await db.execute(
        select(DevelopmentScenario).where(DevelopmentScenario.id.in_(scenario_ids))
    )
    scenarios = result.scalars().all()

    if len(scenarios) < 2:
        raise HTTPException(status_code=400, detail="Need at least 2 scenarios to compare")

    comparison = {
        "scenarios": [],
        "metrics_comparison": {
            "total_cost": {},
            "roi_pct": {},
            "profit": {},
            "timeline_months": {},
            "opportunity_score": {},
        },
    }

    for s in scenarios:
        comparison["scenarios"].append({
            "id": str(s.id),
            "title": s.title,
            "scenario_type": s.scenario_type,
            "total_cost": s.total_cost,
            "roi_pct": s.roi_pct,
            "profit": s.profit,
            "timeline_months": s.timeline_months,
            "opportunity_score": s.opportunity_score,
            "proposed_units": s.proposed_units,
        })
        comparison["metrics_comparison"]["total_cost"][str(s.id)] = s.total_cost
        comparison["metrics_comparison"]["roi_pct"][str(s.id)] = s.roi_pct
        comparison["metrics_comparison"]["profit"][str(s.id)] = s.profit
        comparison["metrics_comparison"]["timeline_months"][str(s.id)] = s.timeline_months
        comparison["metrics_comparison"]["opportunity_score"][str(s.id)] = s.opportunity_score

    # Determine best scenario per metric
    for metric, values in comparison["metrics_comparison"].items():
        if values:
            if metric in ("total_cost", "timeline_months"):
                best_id = min(values, key=values.get)
            else:
                best_id = max(values, key=values.get)
            comparison["metrics_comparison"][metric]["best"] = best_id

    return comparison


@router.patch("/{scenario_id}/prefer")
async def set_preferred_scenario(
    scenario_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Mark a scenario as preferred."""
    result = await db.execute(
        select(DevelopmentScenario).where(DevelopmentScenario.id == scenario_id)
    )
    scenario = result.scalar_one_or_none()
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    # Unset other preferred scenarios for this property
    other_result = await db.execute(
        select(DevelopmentScenario).where(
            DevelopmentScenario.property_id == scenario.property_id,
            DevelopmentScenario.is_preferred == True,
        )
    )
    for other in other_result.scalars().all():
        other.is_preferred = False

    scenario.is_preferred = True
    return {"status": "ok", "scenario_id": str(scenario_id)}
