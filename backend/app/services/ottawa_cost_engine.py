"""
Ottawa Cost Estimation Engine.

Provides Ottawa-specific construction costs, development charges,
soft costs, teardown costs, financing, and tax calculations for 2024.
"""

from dataclasses import dataclass
from enum import Enum

import numpy as np


class ConstructionType(str, Enum):
    WOODFRAME = "woodframe"
    CONCRETE = "concrete"
    STEEL = "steel"
    HYBRID = "hybrid"


class DevelopmentType(str, Enum):
    SINGLE_FAMILY = "single_family"
    DUPLEX = "duplex"
    TOWNHOUSE = "townhouse"
    LOW_RISE_APARTMENT = "low_rise_apartment"
    MID_RISE_APARTMENT = "mid_rise_apartment"
    HIGH_RISE_APARTMENT = "high_rise_apartment"
    COMMERCIAL_RETAIL = "commercial_retail"
    MIXED_USE = "mixed_use"


@dataclass
class OttawaCostParams:
    """2024 Ottawa-specific cost parameters."""

    # Hard construction costs per sq ft
    CONSTRUCTION_COST_PER_SQFT = {
        ConstructionType.WOODFRAME: {"low": 200.0, "mid": 275.0, "high": 350.0},
        ConstructionType.CONCRETE: {"low": 300.0, "mid": 400.0, "high": 500.0},
        ConstructionType.STEEL: {"low": 350.0, "mid": 450.0, "high": 550.0},
        ConstructionType.HYBRID: {"low": 275.0, "mid": 350.0, "high": 425.0},
    }

    # Ottawa Development Charges (2024 rates)
    # Per unit based on type
    DEVELOPMENT_CHARGES_PER_UNIT = {
        DevelopmentType.SINGLE_FAMILY: 43303.0,
        DevelopmentType.DUPLEX: 32000.0,
        DevelopmentType.TOWNHOUSE: 32000.0,
        DevelopmentType.LOW_RISE_APARTMENT: 22500.0,
        DevelopmentType.MID_RISE_APARTMENT: 22500.0,
        DevelopmentType.HIGH_RISE_APARTMENT: 22500.0,
        DevelopmentType.COMMERCIAL_RETAIL: 15.50,  # per sq ft of GFA
        DevelopmentType.MIXED_USE: 22500.0,  # residential portion per unit
    }

    # Teardown costs
    TEARDOWN_COST_RANGE = {"low": 15000.0, "mid": 22500.0, "high": 30000.0}
    HAZMAT_SURCHARGE = {"asbestos": 5000.0, "lead": 3000.0, "mold": 2000.0}

    # Soft cost percentages (of hard construction costs)
    ARCHITECT_FEE_PCT = {"low": 0.08, "mid": 0.10, "high": 0.12}
    ENGINEERING_FEE_PCT = {"low": 0.03, "mid": 0.04, "high": 0.05}
    LEGAL_FEES = {"low": 5000.0, "mid": 10000.0, "high": 20000.0}
    SURVEY_COST = 3500.0
    SITE_PLAN_APPROVAL = {"low": 5000.0, "mid": 12000.0, "high": 25000.0}
    PROJECT_MANAGEMENT_PCT = 0.05

    # Permit fees (City of Ottawa 2024)
    BUILDING_PERMIT_PER_SQFT = 1.75  # approximate
    PLANNING_APPLICATION_FEE = {
        "minor_variance": 2100.0,
        "site_plan_control": 14500.0,
        "rezoning": 22000.0,
        "severance": 3200.0,
    }

    # Financing
    PRIME_RATE = 0.0695  # Bank of Canada Q1 2024
    CONSTRUCTION_LOAN_SPREAD = 0.025
    MORTGAGE_SPREAD = 0.015

    # Taxes
    HST_RATE = 0.13
    HST_NEW_HOUSING_REBATE_THRESHOLD = 450000.0
    HST_REBATE_PCT = 0.36  # federal portion rebate

    # Property tax rate (City of Ottawa 2024 residential)
    PROPERTY_TAX_RATE_RESIDENTIAL = 0.01098659
    PROPERTY_TAX_RATE_COMMERCIAL = 0.02862050

    # Insurance and contingency
    BUILDERS_RISK_INSURANCE_PCT = 0.005
    CONTINGENCY_PCT = 0.10

    # Market data - Ottawa average prices per sq ft (2024)
    SALE_PRICE_PER_SQFT = {
        DevelopmentType.SINGLE_FAMILY: {"low": 350.0, "mid": 425.0, "high": 550.0},
        DevelopmentType.DUPLEX: {"low": 325.0, "mid": 400.0, "high": 500.0},
        DevelopmentType.TOWNHOUSE: {"low": 300.0, "mid": 375.0, "high": 475.0},
        DevelopmentType.LOW_RISE_APARTMENT: {"low": 325.0, "mid": 400.0, "high": 525.0},
        DevelopmentType.MID_RISE_APARTMENT: {"low": 350.0, "mid": 450.0, "high": 600.0},
        DevelopmentType.HIGH_RISE_APARTMENT: {"low": 400.0, "mid": 525.0, "high": 700.0},
        DevelopmentType.COMMERCIAL_RETAIL: {"low": 250.0, "mid": 350.0, "high": 500.0},
        DevelopmentType.MIXED_USE: {"low": 325.0, "mid": 425.0, "high": 575.0},
    }

    # Rental rates per sq ft per month (Ottawa 2024)
    RENTAL_RATE_PER_SQFT_MONTHLY = {
        DevelopmentType.LOW_RISE_APARTMENT: {"low": 1.75, "mid": 2.25, "high": 2.75},
        DevelopmentType.MID_RISE_APARTMENT: {"low": 2.00, "mid": 2.50, "high": 3.00},
        DevelopmentType.HIGH_RISE_APARTMENT: {"low": 2.25, "mid": 2.75, "high": 3.50},
        DevelopmentType.COMMERCIAL_RETAIL: {"low": 1.50, "mid": 2.50, "high": 4.00},
    }


COSTS = OttawaCostParams()


def estimate_construction_cost(
    gfa_sqft: float,
    construction_type: ConstructionType = ConstructionType.WOODFRAME,
    quality: str = "mid",
) -> dict:
    """Estimate hard construction costs."""
    cost_per_sqft = COSTS.CONSTRUCTION_COST_PER_SQFT[construction_type][quality]
    total = gfa_sqft * cost_per_sqft
    return {
        "construction_type": construction_type.value,
        "gfa_sqft": gfa_sqft,
        "cost_per_sqft": cost_per_sqft,
        "total": round(total, 2),
    }


def estimate_teardown_cost(
    existing_gfa_sqft: float,
    hazmat: list[str] | None = None,
    quality: str = "mid",
) -> dict:
    """Estimate demolition/teardown costs."""
    base_cost = COSTS.TEARDOWN_COST_RANGE[quality]

    # Scale for larger structures
    if existing_gfa_sqft > 2000:
        size_factor = 1.0 + (existing_gfa_sqft - 2000) / 5000 * 0.5
        base_cost *= size_factor

    hazmat_cost = 0.0
    hazmat_items = []
    if hazmat:
        for item in hazmat:
            if item in COSTS.HAZMAT_SURCHARGE:
                hazmat_cost += COSTS.HAZMAT_SURCHARGE[item]
                hazmat_items.append({"material": item, "cost": COSTS.HAZMAT_SURCHARGE[item]})

    total = base_cost + hazmat_cost
    return {
        "base_cost": round(base_cost, 2),
        "hazmat_cost": round(hazmat_cost, 2),
        "hazmat_items": hazmat_items,
        "total": round(total, 2),
    }


def estimate_soft_costs(
    hard_construction_cost: float,
    development_type: DevelopmentType,
    num_units: int,
    gfa_sqft: float,
    requires_variance: bool = False,
    requires_rezoning: bool = False,
    requires_site_plan: bool = False,
    quality: str = "mid",
) -> dict:
    """Estimate all soft costs: architect, engineering, legal, permits, DCs."""
    architect = hard_construction_cost * COSTS.ARCHITECT_FEE_PCT[quality]
    engineering = hard_construction_cost * COSTS.ENGINEERING_FEE_PCT[quality]
    legal = COSTS.LEGAL_FEES[quality]
    survey = COSTS.SURVEY_COST
    project_mgmt = hard_construction_cost * COSTS.PROJECT_MANAGEMENT_PCT
    site_plan = COSTS.SITE_PLAN_APPROVAL[quality] if requires_site_plan else 0

    # Building permit
    building_permit = gfa_sqft * COSTS.BUILDING_PERMIT_PER_SQFT

    # Planning application fees
    planning_fees = 0.0
    if requires_variance:
        planning_fees += COSTS.PLANNING_APPLICATION_FEE["minor_variance"]
    if requires_rezoning:
        planning_fees += COSTS.PLANNING_APPLICATION_FEE["rezoning"]
    if requires_site_plan:
        planning_fees += COSTS.PLANNING_APPLICATION_FEE["site_plan_control"]

    # Development charges
    dc_rate = COSTS.DEVELOPMENT_CHARGES_PER_UNIT.get(development_type, 22500.0)
    if development_type == DevelopmentType.COMMERCIAL_RETAIL:
        development_charges = dc_rate * gfa_sqft
    else:
        development_charges = dc_rate * num_units

    # Insurance and contingency
    insurance = hard_construction_cost * COSTS.BUILDERS_RISK_INSURANCE_PCT
    contingency = hard_construction_cost * COSTS.CONTINGENCY_PCT

    total = (
        architect + engineering + legal + survey + project_mgmt +
        site_plan + building_permit + planning_fees +
        development_charges + insurance + contingency
    )

    return {
        "architect": round(architect, 2),
        "engineering": round(engineering, 2),
        "legal": round(legal, 2),
        "survey": round(survey, 2),
        "project_management": round(project_mgmt, 2),
        "site_plan_approval": round(site_plan, 2),
        "building_permit": round(building_permit, 2),
        "planning_fees": round(planning_fees, 2),
        "development_charges": round(development_charges, 2),
        "insurance": round(insurance, 2),
        "contingency": round(contingency, 2),
        "total": round(total, 2),
    }


def estimate_financing_cost(
    total_project_cost: float,
    construction_months: int,
    down_payment_pct: float = 0.25,
    interest_rate: float | None = None,
) -> dict:
    """Estimate financing/carry costs during construction."""
    if interest_rate is None:
        interest_rate = COSTS.PRIME_RATE + COSTS.CONSTRUCTION_LOAN_SPREAD

    loan_amount = total_project_cost * (1 - down_payment_pct)
    # Average outstanding balance during construction (draw schedule)
    avg_balance = loan_amount * 0.6  # Average 60% drawn
    monthly_rate = interest_rate / 12
    total_interest = avg_balance * monthly_rate * construction_months

    # Property taxes during construction
    property_tax_annual = total_project_cost * 0.3 * COSTS.PROPERTY_TAX_RATE_RESIDENTIAL
    property_tax = property_tax_annual * (construction_months / 12)

    total = total_interest + property_tax

    return {
        "loan_amount": round(loan_amount, 2),
        "interest_rate": round(interest_rate, 4),
        "construction_months": construction_months,
        "interest_cost": round(total_interest, 2),
        "property_tax_during_construction": round(property_tax, 2),
        "total": round(total, 2),
    }


def estimate_hst(
    sale_price_per_unit: float,
    num_units: int,
    is_new_construction: bool = True,
) -> dict:
    """Calculate HST liability on new construction."""
    if not is_new_construction:
        return {"total": 0.0, "details": "No HST on resale"}

    total_hst = 0.0
    rebate = 0.0

    for _ in range(num_units):
        unit_hst = sale_price_per_unit * COSTS.HST_RATE
        unit_rebate = 0.0
        if sale_price_per_unit <= COSTS.HST_NEW_HOUSING_REBATE_THRESHOLD:
            # Federal rebate (36% of federal portion = 5%)
            federal_portion = sale_price_per_unit * 0.05
            unit_rebate = federal_portion * COSTS.HST_REBATE_PCT
            # Ontario rebate (75% of provincial portion up to $24,000)
            provincial_portion = sale_price_per_unit * 0.08
            ontario_rebate = min(provincial_portion * 0.75, 24000.0)
            unit_rebate += ontario_rebate

        total_hst += unit_hst
        rebate += unit_rebate

    net_hst = total_hst - rebate
    return {
        "gross_hst": round(total_hst, 2),
        "rebate": round(rebate, 2),
        "net_hst": round(net_hst, 2),
        "total": round(net_hst, 2),
    }


def estimate_revenue(
    development_type: DevelopmentType,
    gfa_sqft: float,
    num_units: int,
    quality: str = "mid",
    is_rental: bool = False,
) -> dict:
    """Estimate sale or rental revenue."""
    result: dict = {"development_type": development_type.value, "num_units": num_units}

    if is_rental and development_type in COSTS.RENTAL_RATE_PER_SQFT_MONTHLY:
        rate = COSTS.RENTAL_RATE_PER_SQFT_MONTHLY[development_type][quality]
        monthly = gfa_sqft * rate
        annual = monthly * 12
        # Assume 5% vacancy
        effective_annual = annual * 0.95
        result["rental_rate_per_sqft_monthly"] = rate
        result["gross_monthly_rental"] = round(monthly, 2)
        result["gross_annual_rental"] = round(annual, 2)
        result["vacancy_rate"] = 0.05
        result["effective_annual_rental"] = round(effective_annual, 2)
        # Operating expenses ~35% of gross
        noi = effective_annual * 0.65
        result["operating_expense_ratio"] = 0.35
        result["net_operating_income"] = round(noi, 2)
    else:
        price_per_sqft = COSTS.SALE_PRICE_PER_SQFT.get(
            development_type,
            COSTS.SALE_PRICE_PER_SQFT[DevelopmentType.LOW_RISE_APARTMENT],
        )[quality]
        total_revenue = gfa_sqft * price_per_sqft
        result["sale_price_per_sqft"] = price_per_sqft
        result["total_sale_revenue"] = round(total_revenue, 2)
        result["avg_unit_price"] = round(total_revenue / max(num_units, 1), 2)

    return result


def calculate_roi_metrics(
    total_cost: float,
    sale_revenue: float | None = None,
    annual_noi: float | None = None,
    equity_invested: float | None = None,
    hold_years: int = 1,
) -> dict:
    """Calculate ROI, IRR, cap rate, and cash-on-cash return."""
    metrics: dict = {}

    if equity_invested is None:
        equity_invested = total_cost * 0.25

    if sale_revenue:
        profit = sale_revenue - total_cost
        metrics["profit"] = round(profit, 2)
        metrics["profit_margin_pct"] = round((profit / sale_revenue) * 100, 2)
        metrics["roi_pct"] = round((profit / total_cost) * 100, 2)

        # Simple IRR approximation for single period
        if hold_years > 0:
            irr = (sale_revenue / total_cost) ** (1 / hold_years) - 1
            metrics["irr_pct"] = round(irr * 100, 2)

    if annual_noi:
        metrics["cap_rate_pct"] = round((annual_noi / total_cost) * 100, 2)
        annual_debt_service = (total_cost - equity_invested) * 0.06  # approximate
        cash_flow = annual_noi - annual_debt_service
        if equity_invested > 0:
            metrics["cash_on_cash_pct"] = round((cash_flow / equity_invested) * 100, 2)

    return metrics


def run_sensitivity_analysis(
    base_costs: dict,
    base_revenue: float,
    num_simulations: int = 1000,
) -> list[dict]:
    """Run Monte Carlo sensitivity analysis on key variables."""
    rng = np.random.default_rng(42)

    variables = {
        "construction_cost": {
            "base": base_costs.get("hard_construction", 0),
            "std_pct": 0.15,
        },
        "sale_price": {
            "base": base_revenue,
            "std_pct": 0.12,
        },
        "timeline_months": {
            "base": base_costs.get("timeline_months", 18),
            "std_pct": 0.25,
        },
        "interest_rate": {
            "base": COSTS.PRIME_RATE + COSTS.CONSTRUCTION_LOAN_SPREAD,
            "std_pct": 0.20,
        },
    }

    base_profit = base_revenue - sum(
        v for k, v in base_costs.items()
        if isinstance(v, (int, float)) and k != "timeline_months"
    )
    base_roi = (base_profit / max(base_revenue, 1)) * 100

    results = []
    for var_name, params in variables.items():
        simulated = rng.normal(params["base"], params["base"] * params["std_pct"], num_simulations)
        low = float(np.percentile(simulated, 10))
        high = float(np.percentile(simulated, 90))

        # Estimate ROI impact
        if var_name in ("construction_cost", "interest_rate", "timeline_months"):
            low_roi = base_roi + (params["base"] - high) / max(base_revenue, 1) * 100
            high_roi = base_roi + (params["base"] - low) / max(base_revenue, 1) * 100
        else:
            low_roi = base_roi - (params["base"] - low) / max(base_revenue, 1) * 100
            high_roi = base_roi + (high - params["base"]) / max(base_revenue, 1) * 100

        results.append({
            "variable": var_name,
            "base_value": round(params["base"], 2),
            "low_case": round(low, 2),
            "high_case": round(high, 2),
            "impact_on_roi_pct": round(abs(high_roi - low_roi) / 2, 2),
        })

    return results


def generate_full_cost_estimate(
    acquisition_cost: float,
    gfa_sqft: float,
    num_units: int,
    development_type: DevelopmentType,
    construction_type: ConstructionType = ConstructionType.WOODFRAME,
    construction_months: int = 18,
    existing_gfa_sqft: float = 0,
    requires_teardown: bool = True,
    requires_variance: bool = False,
    requires_rezoning: bool = False,
    requires_site_plan: bool = True,
    is_rental: bool = False,
    quality: str = "mid",
    down_payment_pct: float = 0.25,
    hazmat: list[str] | None = None,
) -> dict:
    """Generate a comprehensive cost estimate for a development project."""
    # Hard costs
    construction = estimate_construction_cost(gfa_sqft, construction_type, quality)
    hard_cost = construction["total"]

    # Teardown
    teardown = estimate_teardown_cost(existing_gfa_sqft, hazmat, quality) if requires_teardown else {"total": 0}

    # Soft costs
    soft = estimate_soft_costs(
        hard_cost, development_type, num_units, gfa_sqft,
        requires_variance, requires_rezoning, requires_site_plan, quality,
    )

    # Subtotal before financing
    subtotal = acquisition_cost + teardown["total"] + hard_cost + soft["total"]

    # Financing
    financing = estimate_financing_cost(subtotal, construction_months, down_payment_pct)

    # Revenue
    revenue = estimate_revenue(development_type, gfa_sqft, num_units, quality, is_rental)

    # HST
    if is_rental:
        hst = {"total": 0.0, "details": "Input tax credits available for rental"}
    else:
        avg_unit_price = revenue.get("avg_unit_price", 0)
        hst = estimate_hst(avg_unit_price, num_units)

    # Total cost
    total_cost = subtotal + financing["total"] + hst["total"]

    # ROI
    sale_revenue = revenue.get("total_sale_revenue")
    annual_noi = revenue.get("net_operating_income")
    equity = total_cost * down_payment_pct
    roi = calculate_roi_metrics(total_cost, sale_revenue, annual_noi, equity)

    # Sensitivity
    sensitivity_inputs = {
        "hard_construction": hard_cost,
        "soft_costs": soft["total"],
        "financing": financing["total"],
        "timeline_months": construction_months,
    }
    base_rev = sale_revenue or (annual_noi * 15 if annual_noi else total_cost)
    sensitivity = run_sensitivity_analysis(sensitivity_inputs, base_rev)

    return {
        "acquisition_cost": acquisition_cost,
        "teardown": teardown,
        "construction": construction,
        "soft_costs": soft,
        "financing": financing,
        "hst": hst,
        "total_cost": round(total_cost, 2),
        "revenue": revenue,
        "roi_metrics": roi,
        "sensitivity_analysis": sensitivity,
        "summary": {
            "total_investment": round(total_cost, 2),
            "equity_required": round(equity, 2),
            "debt": round(total_cost - equity, 2),
        },
    }
