"""
AI Analysis Service.

Uses OpenAI GPT-4 with function calling to generate development scenarios
and feasibility assessments from property and zoning data.
"""

import hashlib
import json
from datetime import datetime, timezone

from openai import AsyncOpenAI

from app.core.cache import get_cached, set_cached
from app.core.config import settings
from app.services.ottawa_cost_engine import (
    ConstructionType,
    DevelopmentType,
    generate_full_cost_estimate,
)
from app.services.zoning_parser import (
    ZoningEnvelope,
    calculate_development_potential,
    map_zone_to_development_types,
)

client = AsyncOpenAI(api_key=settings.openai_api_key)

SYSTEM_PROMPT = """You are an expert real estate development analyst specializing in Ottawa, Ontario, Canada.
You analyze property data, zoning bylaws, and market conditions to generate feasible development scenarios.

Your analysis must be:
1. Grounded in Ottawa's Zoning By-law 2008-250
2. Realistic based on current Ottawa construction costs and market values
3. Conservative in projections (use mid-range estimates)
4. Clear about risks, required approvals, and potential variances

Always consider:
- Heritage designations and adjacency
- Floodplain and environmental constraints
- Parking requirements and potential reductions
- Development charge implications
- Timeline risks (permit delays, seasonal construction)
- Ottawa-specific market conditions

Output structured JSON matching the required schema."""

ANALYSIS_PROMPT_TEMPLATE = """Analyze this Ottawa property for development potential and generate feasible scenarios.

## Property Data
- Address: {address}
- Parcel ID: {parcel_id}
- Lot Size: {lot_width_ft}ft x {lot_depth_ft}ft ({lot_area_sqft} sq ft)
- Current Use: {current_use}
- Current Structure: {structure_type}, built {year_built}
- Assessed Value: ${assessed_value:,.0f}
- Zoning: {zoning_code}

## Zoning Analysis
{zoning_analysis}

## Development Potential
{development_potential}

## Constraints
- Heritage Designated: {is_heritage}
- Floodplain: {is_floodplain}
- Easements: {has_easements}
- Environmental: {environmental_constraints}

## Target Use
{target_use}

## Acquisition Cost
${acquisition_cost:,.0f}

## Instructions
Generate 2-4 development scenarios ranked by feasibility. For each scenario, provide:
1. Scenario type and description
2. Proposed unit count, storeys, and GFA
3. Whether it requires teardown, variance, rezoning, or site plan approval
4. Construction type recommendation
5. Key risks specific to this property
6. Estimated timeline in months
7. Overall opportunity score (0-100)
8. Confidence level (high/medium/low)

Consider the highest-and-best-use principle. Evaluate teardown vs renovation.
For the target use "{target_use}", prioritize scenarios that align with this goal."""

# GPT-4 function calling schema for structured output
SCENARIO_FUNCTION = {
    "name": "generate_development_scenarios",
    "description": "Generate structured development scenarios for a property",
    "parameters": {
        "type": "object",
        "properties": {
            "zoning_summary": {
                "type": "string",
                "description": "Plain-language summary of zoning implications",
            },
            "highest_best_use": {
                "type": "string",
                "description": "Recommended highest and best use for the property",
            },
            "scenarios": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "scenario_type": {
                            "type": "string",
                            "enum": [
                                "teardown_new_construction",
                                "renovation_conversion",
                                "addition_expansion",
                                "mixed_use_development",
                                "commercial_development",
                                "land_assembly",
                            ],
                        },
                        "title": {"type": "string"},
                        "description": {"type": "string"},
                        "target_use": {
                            "type": "string",
                            "enum": [
                                "single_family",
                                "duplex",
                                "townhouse",
                                "low_rise_apartment",
                                "mid_rise_apartment",
                                "high_rise_apartment",
                                "commercial_retail",
                                "mixed_use",
                            ],
                        },
                        "proposed_units": {"type": "integer"},
                        "proposed_storeys": {"type": "integer"},
                        "proposed_gfa_sqft": {"type": "number"},
                        "construction_type": {
                            "type": "string",
                            "enum": ["woodframe", "concrete", "steel", "hybrid"],
                        },
                        "requires_teardown": {"type": "boolean"},
                        "requires_variance": {"type": "boolean"},
                        "requires_rezoning": {"type": "boolean"},
                        "requires_site_plan": {"type": "boolean"},
                        "construction_months": {"type": "integer"},
                        "risks": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "opportunity_score": {"type": "number", "minimum": 0, "maximum": 100},
                        "confidence_level": {
                            "type": "string",
                            "enum": ["high", "medium", "low"],
                        },
                    },
                    "required": [
                        "scenario_type", "title", "description", "target_use",
                        "proposed_units", "proposed_storeys", "proposed_gfa_sqft",
                        "construction_type", "requires_teardown", "construction_months",
                        "risks", "opportunity_score", "confidence_level",
                    ],
                },
            },
        },
        "required": ["zoning_summary", "highest_best_use", "scenarios"],
    },
}


def _build_prompt(property_data: dict, zoning_envelope: ZoningEnvelope | None, dev_potential: dict) -> str:
    """Build the analysis prompt from property data."""
    zoning_analysis = "No zoning data available."
    if zoning_envelope:
        zoning_analysis = (
            f"Zone: {zoning_envelope.zone_code} ({zoning_envelope.zone_category.value})\n"
            f"Permitted Uses: {', '.join(zoning_envelope.permitted_uses)}\n"
            f"Max Height: {zoning_envelope.max_height_m}m\n"
            f"Max Storeys: {zoning_envelope.max_storeys}\n"
            f"Max FSI: {zoning_envelope.max_fsi}\n"
            f"Max Lot Coverage: {zoning_envelope.max_lot_coverage_pct}%\n"
            f"Setbacks: Front {zoning_envelope.front_setback_m}m, "
            f"Rear {zoning_envelope.rear_setback_m}m, "
            f"Side {zoning_envelope.interior_side_setback_m}m\n"
            f"Parking: {zoning_envelope.min_parking_spaces_per_unit} spaces/unit"
        )

    dev_potential_text = json.dumps(dev_potential, indent=2)

    return ANALYSIS_PROMPT_TEMPLATE.format(
        address=property_data.get("address", "Unknown"),
        parcel_id=property_data.get("parcel_id", "Unknown"),
        lot_width_ft=property_data.get("lot_width_ft", "N/A"),
        lot_depth_ft=property_data.get("lot_depth_ft", "N/A"),
        lot_area_sqft=property_data.get("lot_area_sqft", 0),
        current_use=property_data.get("current_use", "Unknown"),
        structure_type=property_data.get("structure_type", "Unknown"),
        year_built=property_data.get("year_built", "Unknown"),
        assessed_value=property_data.get("assessed_value", 0),
        zoning_code=property_data.get("zoning_code", "Unknown"),
        zoning_analysis=zoning_analysis,
        development_potential=dev_potential_text,
        is_heritage=property_data.get("is_heritage", False),
        is_floodplain=property_data.get("is_floodplain", False),
        has_easements=property_data.get("has_easements", False),
        environmental_constraints=property_data.get("environmental_constraints", "None"),
        target_use=property_data.get("target_use", "multi_unit_rental"),
        acquisition_cost=property_data.get("acquisition_cost", 0),
    )


async def generate_scenarios(
    property_data: dict,
    zoning_envelope: ZoningEnvelope | None,
    dev_potential: dict,
) -> dict:
    """Use GPT-4 to generate development scenarios for a property."""
    prompt = _build_prompt(property_data, zoning_envelope, dev_potential)
    prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()[:16]

    # Check cache
    cache_key = f"ai_analysis:{prompt_hash}"
    cached = await get_cached(cache_key)
    if cached:
        return cached

    response = await client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        functions=[SCENARIO_FUNCTION],
        function_call={"name": "generate_development_scenarios"},
        temperature=0.3,
        max_tokens=4000,
    )

    message = response.choices[0].message
    if message.function_call:
        ai_result = json.loads(message.function_call.arguments)
    else:
        ai_result = {
            "zoning_summary": "Unable to generate AI analysis.",
            "highest_best_use": "Manual review required.",
            "scenarios": [],
        }

    # Enrich scenarios with cost estimates
    enriched_scenarios = []
    for scenario in ai_result.get("scenarios", []):
        try:
            cost_estimate = generate_full_cost_estimate(
                acquisition_cost=property_data.get("acquisition_cost", 0),
                gfa_sqft=scenario.get("proposed_gfa_sqft", 0),
                num_units=scenario.get("proposed_units", 1),
                development_type=DevelopmentType(scenario.get("target_use", "low_rise_apartment")),
                construction_type=ConstructionType(scenario.get("construction_type", "woodframe")),
                construction_months=scenario.get("construction_months", 18),
                existing_gfa_sqft=property_data.get("gross_floor_area_sqft", 0),
                requires_teardown=scenario.get("requires_teardown", True),
                requires_variance=scenario.get("requires_variance", False),
                requires_rezoning=scenario.get("requires_rezoning", False),
                requires_site_plan=scenario.get("requires_site_plan", True),
                is_rental="rental" in property_data.get("target_use", ""),
            )
            scenario["cost_estimate"] = cost_estimate
        except (ValueError, KeyError):
            scenario["cost_estimate"] = None

        enriched_scenarios.append(scenario)

    result = {
        "zoning_summary": ai_result.get("zoning_summary", ""),
        "highest_best_use": ai_result.get("highest_best_use", ""),
        "scenarios": enriched_scenarios,
        "ai_model": settings.openai_model,
        "prompt_hash": prompt_hash,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }

    # Cache for 6 hours
    await set_cached(cache_key, result, ttl=21600)

    return result


def build_analysis_response(
    property_data: dict,
    zoning_envelope: ZoningEnvelope | None,
    dev_potential: dict,
    ai_result: dict,
) -> dict:
    """Build the final analysis response combining all data."""
    scenarios = []
    for s in ai_result.get("scenarios", []):
        cost_est = s.get("cost_estimate", {})
        roi_metrics = cost_est.get("roi_metrics", {}) if cost_est else {}
        revenue = cost_est.get("revenue", {}) if cost_est else {}

        scenario = {
            "scenario_type": s.get("scenario_type"),
            "title": s.get("title"),
            "description": s.get("description"),
            "target_use": s.get("target_use"),
            "proposed_units": s.get("proposed_units"),
            "proposed_storeys": s.get("proposed_storeys"),
            "proposed_gfa_sqft": s.get("proposed_gfa_sqft"),
            "costs": {
                "acquisition": property_data.get("acquisition_cost", 0),
                "teardown": cost_est.get("teardown", {}).get("total", 0) if cost_est else 0,
                "hard_construction": cost_est.get("construction", {}).get("total", 0) if cost_est else 0,
                "soft_costs": cost_est.get("soft_costs", {}).get("total", 0) if cost_est else 0,
                "development_charges": cost_est.get("soft_costs", {}).get("development_charges", 0) if cost_est else 0,
                "permit_fees": cost_est.get("soft_costs", {}).get("building_permit", 0) if cost_est else 0,
                "financing": cost_est.get("financing", {}).get("total", 0) if cost_est else 0,
                "hst": cost_est.get("hst", {}).get("total", 0) if cost_est else 0,
                "total": cost_est.get("total_cost", 0) if cost_est else 0,
            },
            "projected_sale_revenue": revenue.get("total_sale_revenue"),
            "projected_annual_rental": revenue.get("effective_annual_rental"),
            "roi_metrics": {
                "profit": roi_metrics.get("profit", 0),
                "profit_margin_pct": roi_metrics.get("profit_margin_pct", 0),
                "roi_pct": roi_metrics.get("roi_pct", 0),
                "irr_pct": roi_metrics.get("irr_pct"),
                "cap_rate_pct": roi_metrics.get("cap_rate_pct"),
                "cash_on_cash_pct": roi_metrics.get("cash_on_cash_pct"),
            },
            "timeline_months": s.get("construction_months", 18),
            "risks": s.get("risks", []),
            "opportunity_score": s.get("opportunity_score", 50),
            "confidence_level": s.get("confidence_level", "medium"),
            "sensitivity_analysis": cost_est.get("sensitivity_analysis") if cost_est else None,
        }
        scenarios.append(scenario)

    # Overall opportunity score: weighted average of scenarios
    if scenarios:
        overall_score = sum(s["opportunity_score"] for s in scenarios) / len(scenarios)
    else:
        overall_score = 0

    return {
        "property_id": property_data.get("id"),
        "address": property_data.get("address"),
        "parcel_id": property_data.get("parcel_id"),
        "zoning_code": property_data.get("zoning_code", "Unknown"),
        "zoning_summary": ai_result.get("zoning_summary", ""),
        "lot_area_sqft": property_data.get("lot_area_sqft", 0),
        "overall_opportunity_score": round(overall_score, 1),
        "scenarios": scenarios,
        "generated_at": ai_result.get("generated_at"),
    }
