import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ZoningRule(Base):
    __tablename__ = "zoning_rules"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    property_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("properties.id", ondelete="CASCADE"), index=True
    )

    # Zoning classification
    zone_code: Mapped[str] = mapped_column(String(20), index=True)
    zone_category: Mapped[str] = mapped_column(String(50))  # residential, commercial, mixed
    zone_suffix: Mapped[str | None] = mapped_column(String(20))  # e.g., R4[2.0]
    bylaw_reference: Mapped[str] = mapped_column(
        String(50), default="2008-250"
    )

    # Permitted uses
    permitted_uses: Mapped[dict | None] = mapped_column(JSONB)
    conditional_uses: Mapped[dict | None] = mapped_column(JSONB)

    # Building envelope
    max_height_m: Mapped[float | None] = mapped_column(Float)
    max_storeys: Mapped[int | None] = mapped_column(Integer)
    max_fsi: Mapped[float | None] = mapped_column(Float)  # Floor Space Index
    max_lot_coverage_pct: Mapped[float | None] = mapped_column(Float)
    max_density_units_per_ha: Mapped[float | None] = mapped_column(Float)

    # Setbacks (metres)
    front_setback_m: Mapped[float | None] = mapped_column(Float)
    rear_setback_m: Mapped[float | None] = mapped_column(Float)
    interior_side_setback_m: Mapped[float | None] = mapped_column(Float)
    exterior_side_setback_m: Mapped[float | None] = mapped_column(Float)

    # Parking & amenity
    min_parking_spaces: Mapped[int | None] = mapped_column(Integer)
    min_bicycle_parking: Mapped[int | None] = mapped_column(Integer)
    min_amenity_area_sqm: Mapped[float | None] = mapped_column(Float)
    min_landscaped_area_pct: Mapped[float | None] = mapped_column(Float)

    # Development potential
    max_buildable_area_sqft: Mapped[float | None] = mapped_column(Float)
    max_units: Mapped[int | None] = mapped_column(Integer)
    development_potential_summary: Mapped[str | None] = mapped_column(Text)

    # Overlays and exceptions
    overlays: Mapped[dict | None] = mapped_column(JSONB)
    exceptions: Mapped[dict | None] = mapped_column(JSONB)
    secondary_plan: Mapped[str | None] = mapped_column(String(200))

    # Metadata
    source_text: Mapped[str | None] = mapped_column(Text)
    parsed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationship
    property: Mapped["Property"] = relationship(back_populates="zoning_rules")

    def __repr__(self) -> str:
        return f"<ZoningRule(zone_code={self.zone_code}, property_id={self.property_id})>"


from app.models.property import Property  # noqa: E402
