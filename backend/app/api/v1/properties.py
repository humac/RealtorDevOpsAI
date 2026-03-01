"""Property search and retrieval endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.property import Property
from app.schemas.property import (
    PropertyBriefResponse,
    PropertyFilterRequest,
    PropertyResponse,
    PropertySearchRequest,
)

router = APIRouter()


@router.get("/search", response_model=list[PropertyBriefResponse])
async def search_properties(
    q: str = Query(..., description="Search by address, MLS number, or parcel ID"),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Search properties by address, MLS number, or parcel ID."""
    query = select(Property).where(
        (Property.address.ilike(f"%{q}%"))
        | (Property.mls_number == q)
        | (Property.parcel_id == q)
    ).limit(limit)

    result = await db.execute(query)
    properties = result.scalars().all()
    return properties


@router.get("/filter", response_model=list[PropertyBriefResponse])
async def filter_properties(
    ward: str | None = None,
    neighbourhood: str | None = None,
    min_lot_size: float | None = None,
    max_lot_size: float | None = None,
    zoning_code: str | None = None,
    min_assessed_value: float | None = None,
    max_assessed_value: float | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Filter properties by various criteria."""
    query = select(Property)

    if ward:
        query = query.where(Property.ward.ilike(f"%{ward}%"))
    if neighbourhood:
        query = query.where(Property.neighbourhood.ilike(f"%{neighbourhood}%"))
    if min_lot_size:
        query = query.where(Property.lot_area_sqft >= min_lot_size)
    if max_lot_size:
        query = query.where(Property.lot_area_sqft <= max_lot_size)
    if zoning_code:
        query = query.where(Property.zoning_code == zoning_code.upper())
    if min_assessed_value:
        query = query.where(Property.assessed_value >= min_assessed_value)
    if max_assessed_value:
        query = query.where(Property.assessed_value <= max_assessed_value)

    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/nearby", response_model=list[PropertyBriefResponse])
async def get_nearby_properties(
    lat: float = Query(..., description="Latitude"),
    lng: float = Query(..., description="Longitude"),
    radius_km: float = Query(1.0, ge=0.1, le=10.0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Find properties near a geographic point."""
    point = func.ST_SetSRID(func.ST_MakePoint(lng, lat), 4326)
    distance = func.ST_Distance(
        func.ST_Transform(Property.centroid, 32189),
        func.ST_Transform(point, 32189),
    )

    query = (
        select(Property)
        .where(distance <= radius_km * 1000)
        .order_by(distance)
        .limit(limit)
    )

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{property_id}", response_model=PropertyResponse)
async def get_property(
    property_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get detailed property information."""
    result = await db.execute(select(Property).where(Property.id == property_id))
    prop = result.scalar_one_or_none()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    return prop


@router.get("/parcel/{parcel_id}", response_model=PropertyResponse)
async def get_property_by_parcel(
    parcel_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get property by parcel ID."""
    result = await db.execute(select(Property).where(Property.parcel_id == parcel_id))
    prop = result.scalar_one_or_none()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    return prop
