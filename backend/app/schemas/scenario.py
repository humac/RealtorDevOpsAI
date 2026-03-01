from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class CostBreakdown(BaseModel):
    acquisition: float
    teardown: float
    hard_construction: float
    soft_costs: float
    development_charges: float
    permit_fees: float
    financing: float
    hst: float
    total: float


class ROIMetrics(BaseModel):
    profit: float
    profit_margin_pct: float
    roi_pct: float
    irr_pct: float | None
    cap_rate_pct: float | None
    cash_on_cash_pct: float | None


class SensitivityResult(BaseModel):
    variable: str
    base_value: float
    low_case: float
    high_case: float
    impact_on_roi_pct: float


class ScenarioResponse(BaseModel):
    id: UUID | None = None
    scenario_type: str
    title: str
    description: str
    target_use: str
    proposed_units: int | None
    proposed_storeys: int | None
    proposed_gfa_sqft: float | None
    costs: CostBreakdown
    projected_sale_revenue: float | None
    projected_annual_rental: float | None
    roi_metrics: ROIMetrics
    timeline_months: int
    risks: list[str]
    opportunity_score: float
    confidence_level: str
    sensitivity_analysis: list[SensitivityResult] | None = None

    model_config = {"from_attributes": True}


class AnalysisResponse(BaseModel):
    property_id: UUID
    address: str
    parcel_id: str
    zoning_code: str
    zoning_summary: str
    lot_area_sqft: float
    overall_opportunity_score: float
    scenarios: list[ScenarioResponse]
    disclaimer: str = (
        "This AI-generated analysis is for informational purposes only. "
        "It does not constitute legal, financial, or professional advice. "
        "Consult qualified professionals before making investment decisions."
    )
    generated_at: datetime | None = None

    model_config = {"from_attributes": True}
