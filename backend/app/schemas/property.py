from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class PropertySearchRequest(BaseModel):
    address: str | None = None
    mls_number: str | None = None
    parcel_id: str | None = None
    lat: float | None = None
    lng: float | None = None
    radius_km: float = 1.0


class PropertyFilterRequest(BaseModel):
    ward: str | None = None
    neighbourhood: str | None = None
    min_lot_size_sqft: float | None = None
    max_lot_size_sqft: float | None = None
    current_use: str | None = None
    min_assessed_value: float | None = None
    max_assessed_value: float | None = None
    zoning_code: str | None = None
    page: int = 1
    page_size: int = 20


class PropertyResponse(BaseModel):
    id: UUID
    parcel_id: str
    address: str
    city: str
    province: str
    postal_code: str | None
    lot_width_ft: float | None
    lot_depth_ft: float | None
    lot_area_sqft: float | None
    current_use: str | None
    structure_type: str | None
    year_built: int | None
    num_storeys: int | None
    gross_floor_area_sqft: float | None
    num_units: int | None
    assessed_value: float | None
    assessed_land_value: float | None
    assessed_building_value: float | None
    zoning_code: str | None
    zoning_description: str | None
    ward: str | None
    neighbourhood: str | None
    is_heritage: bool
    is_floodplain: bool
    has_easements: bool
    opportunity_score: float | None
    risk_factors: dict | None
    last_updated: datetime

    model_config = {"from_attributes": True}


class PropertyBriefResponse(BaseModel):
    id: UUID
    parcel_id: str
    address: str
    zoning_code: str | None
    lot_area_sqft: float | None
    assessed_value: float | None
    opportunity_score: float | None

    model_config = {"from_attributes": True}


class AnalyzePropertyRequest(BaseModel):
    address: str | None = None
    parcel_id: str | None = None
    acquisition_cost: float | None = None
    target_use: str = Field(
        default="multi_unit_rental",
        description="Target use: single_family, duplex, multi_unit_rental, commercial, mixed_use",
    )
    financing: dict | None = Field(
        default=None,
        description="Custom financing params: {down_payment_pct, interest_rate, amortization_years}",
    )
