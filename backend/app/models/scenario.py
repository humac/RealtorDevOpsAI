import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class DevelopmentScenario(Base):
    __tablename__ = "development_scenarios"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    property_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("properties.id", ondelete="CASCADE"), index=True
    )
    user_id: Mapped[str | None] = mapped_column(String(100), index=True)

    # Scenario details
    scenario_type: Mapped[str] = mapped_column(String(50))
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text)
    target_use: Mapped[str] = mapped_column(String(50))

    # Proposed development
    proposed_units: Mapped[int | None] = mapped_column(Integer)
    proposed_storeys: Mapped[int | None] = mapped_column(Integer)
    proposed_gfa_sqft: Mapped[float | None] = mapped_column(Float)
    proposed_fsi: Mapped[float | None] = mapped_column(Float)

    # Cost breakdown
    acquisition_cost: Mapped[float | None] = mapped_column(Float)
    teardown_cost: Mapped[float | None] = mapped_column(Float)
    hard_construction_cost: Mapped[float | None] = mapped_column(Float)
    soft_costs: Mapped[float | None] = mapped_column(Float)
    development_charges: Mapped[float | None] = mapped_column(Float)
    permit_fees: Mapped[float | None] = mapped_column(Float)
    financing_cost: Mapped[float | None] = mapped_column(Float)
    hst_cost: Mapped[float | None] = mapped_column(Float)
    total_cost: Mapped[float | None] = mapped_column(Float)
    cost_breakdown: Mapped[dict | None] = mapped_column(JSONB)

    # Revenue projections
    projected_sale_revenue: Mapped[float | None] = mapped_column(Float)
    projected_monthly_rental: Mapped[float | None] = mapped_column(Float)
    projected_annual_rental: Mapped[float | None] = mapped_column(Float)
    revenue_assumptions: Mapped[dict | None] = mapped_column(JSONB)

    # ROI metrics
    profit: Mapped[float | None] = mapped_column(Float)
    profit_margin_pct: Mapped[float | None] = mapped_column(Float)
    roi_pct: Mapped[float | None] = mapped_column(Float)
    irr_pct: Mapped[float | None] = mapped_column(Float)
    cap_rate_pct: Mapped[float | None] = mapped_column(Float)
    cash_on_cash_pct: Mapped[float | None] = mapped_column(Float)

    # Timeline
    timeline_months: Mapped[int | None] = mapped_column(Integer)
    construction_start_est: Mapped[str | None] = mapped_column(String(20))

    # Risk assessment
    risks: Mapped[dict | None] = mapped_column(JSONB)
    opportunity_score: Mapped[float | None] = mapped_column(Float)
    confidence_level: Mapped[str | None] = mapped_column(String(20))

    # Sensitivity analysis results
    sensitivity_analysis: Mapped[dict | None] = mapped_column(JSONB)

    # AI generation metadata
    ai_model_used: Mapped[str | None] = mapped_column(String(50))
    ai_prompt_hash: Mapped[str | None] = mapped_column(String(64))
    ai_raw_response: Mapped[dict | None] = mapped_column(JSONB)

    # Metadata
    is_preferred: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationship
    property: Mapped["Property"] = relationship(back_populates="scenarios")

    def __repr__(self) -> str:
        return f"<DevelopmentScenario(type={self.scenario_type}, property_id={self.property_id})>"


from app.models.property import Property  # noqa: E402
