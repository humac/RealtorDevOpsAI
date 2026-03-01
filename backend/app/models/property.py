import uuid
from datetime import datetime

from geoalchemy2 import Geometry
from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Property(Base):
    __tablename__ = "properties"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    parcel_id: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    address: Mapped[str] = mapped_column(String(500), index=True)
    city: Mapped[str] = mapped_column(String(100), default="Ottawa")
    province: Mapped[str] = mapped_column(String(50), default="Ontario")
    postal_code: Mapped[str | None] = mapped_column(String(10))

    # Lot details
    lot_width_ft: Mapped[float | None] = mapped_column(Float)
    lot_depth_ft: Mapped[float | None] = mapped_column(Float)
    lot_area_sqft: Mapped[float | None] = mapped_column(Float)
    lot_area_sqm: Mapped[float | None] = mapped_column(Float)

    # Current structure
    current_use: Mapped[str | None] = mapped_column(String(100))
    structure_type: Mapped[str | None] = mapped_column(String(100))
    year_built: Mapped[int | None] = mapped_column(Integer)
    num_storeys: Mapped[int | None] = mapped_column(Integer)
    gross_floor_area_sqft: Mapped[float | None] = mapped_column(Float)
    num_units: Mapped[int | None] = mapped_column(Integer)

    # Valuation
    assessed_value: Mapped[float | None] = mapped_column(Float)
    assessed_land_value: Mapped[float | None] = mapped_column(Float)
    assessed_building_value: Mapped[float | None] = mapped_column(Float)
    market_value_estimate: Mapped[float | None] = mapped_column(Float)

    # Ownership
    owner_name: Mapped[str | None] = mapped_column(String(500))
    mls_number: Mapped[str | None] = mapped_column(String(20), index=True)

    # Zoning
    zoning_code: Mapped[str | None] = mapped_column(String(20), index=True)
    zoning_description: Mapped[str | None] = mapped_column(Text)
    ward: Mapped[str | None] = mapped_column(String(100))
    neighbourhood: Mapped[str | None] = mapped_column(String(200))

    # Constraints
    is_heritage: Mapped[bool] = mapped_column(Boolean, default=False)
    is_floodplain: Mapped[bool] = mapped_column(Boolean, default=False)
    has_easements: Mapped[bool] = mapped_column(Boolean, default=False)
    environmental_constraints: Mapped[dict | None] = mapped_column(JSONB)

    # Spatial
    geometry: Mapped[str | None] = mapped_column(Geometry("POLYGON", srid=4326))
    centroid: Mapped[str | None] = mapped_column(Geometry("POINT", srid=4326))

    # Opportunity scoring
    opportunity_score: Mapped[float | None] = mapped_column(Float)
    risk_factors: Mapped[dict | None] = mapped_column(JSONB)

    # Metadata
    data_source: Mapped[str | None] = mapped_column(String(100))
    last_updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    raw_data: Mapped[dict | None] = mapped_column(JSONB)

    # Relationships
    zoning_rules: Mapped[list["ZoningRule"]] = relationship(back_populates="property")
    scenarios: Mapped[list["DevelopmentScenario"]] = relationship(back_populates="property")

    __table_args__ = (
        Index("idx_property_geometry", "geometry", postgresql_using="gist"),
        Index("idx_property_centroid", "centroid", postgresql_using="gist"),
    )

    def __repr__(self) -> str:
        return f"<Property(parcel_id={self.parcel_id}, address={self.address})>"


# Import here to avoid circular imports
from app.models.zoning import ZoningRule  # noqa: E402
from app.models.scenario import DevelopmentScenario  # noqa: E402
