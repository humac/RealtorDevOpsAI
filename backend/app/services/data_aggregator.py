"""
Data Aggregation Service.

Fetches and combines property data from Ottawa Open Data, GeoOttawa,
and other external sources.
"""

import httpx

from app.core.cache import get_cached, set_cached
from app.core.config import settings


async def fetch_property_by_address(address: str) -> dict | None:
    """Search for a property by address using Ottawa Open Data."""
    cache_key = f"property:address:{address.lower().strip()}"
    cached = await get_cached(cache_key)
    if cached:
        return cached

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{settings.ottawa_open_data_url}/records/1.0/search/",
                params={
                    "dataset": "property-parcels",
                    "q": address,
                    "rows": 1,
                },
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("records"):
                    result = data["records"][0]["fields"]
                    await set_cached(cache_key, result, ttl=86400)
                    return result
    except httpx.RequestError:
        pass

    return None


async def fetch_property_by_parcel_id(parcel_id: str) -> dict | None:
    """Fetch property data by parcel ID."""
    cache_key = f"property:parcel:{parcel_id}"
    cached = await get_cached(cache_key)
    if cached:
        return cached

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{settings.ottawa_open_data_url}/records/1.0/search/",
                params={
                    "dataset": "property-parcels",
                    "q": f"parcel_id:{parcel_id}",
                    "rows": 1,
                },
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("records"):
                    result = data["records"][0]["fields"]
                    await set_cached(cache_key, result, ttl=86400)
                    return result
    except httpx.RequestError:
        pass

    return None


async def fetch_geo_ottawa_data(parcel_id: str) -> dict | None:
    """Fetch topographic, floodplain, and utility data from GeoOttawa WFS."""
    cache_key = f"geo:parcel:{parcel_id}"
    cached = await get_cached(cache_key)
    if cached:
        return cached

    layers = {
        "floodplain": "Floodplain",
        "heritage": "Heritage_Buildings",
        "topography": "Contours",
        "easements": "Easements",
    }

    result: dict = {}
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            for key, layer_name in layers.items():
                response = await client.get(
                    settings.geo_ottawa_wfs_url,
                    params={
                        "service": "WFS",
                        "version": "2.0.0",
                        "request": "GetFeature",
                        "typeName": layer_name,
                        "CQL_FILTER": f"PARCEL_ID='{parcel_id}'",
                        "outputFormat": "application/json",
                        "count": 10,
                    },
                )
                if response.status_code == 200:
                    data = response.json()
                    features = data.get("features", [])
                    result[key] = {
                        "found": len(features) > 0,
                        "count": len(features),
                        "features": features[:3],
                    }
                else:
                    result[key] = {"found": False, "count": 0, "features": []}
    except httpx.RequestError:
        pass

    if result:
        await set_cached(cache_key, result, ttl=86400)

    return result or None


async def fetch_comparable_sales(
    lat: float,
    lng: float,
    radius_km: float = 1.0,
    property_type: str = "residential",
) -> list[dict]:
    """Fetch comparable sales data near a location."""
    cache_key = f"comps:{lat:.4f}:{lng:.4f}:{radius_km}:{property_type}"
    cached = await get_cached(cache_key)
    if cached:
        return cached

    # Placeholder for Realtor API or web scraping integration
    # In production, this would connect to Realtor.ca API or CMHC data
    comps: list[dict] = []

    if comps:
        await set_cached(cache_key, comps, ttl=43200)

    return comps


async def fetch_development_charges_schedule() -> dict:
    """Fetch current Ottawa development charges schedule."""
    cache_key = "ottawa:dc_schedule:2024"
    cached = await get_cached(cache_key)
    if cached:
        return cached

    # Ottawa DC schedule - these would be fetched from open data in production
    schedule = {
        "effective_date": "2024-01-01",
        "residential": {
            "single_detached": 43303,
            "semi_detached": 32000,
            "townhouse": 32000,
            "apartment_2plus_bedrooms": 22500,
            "apartment_bachelor_1bed": 14800,
        },
        "non_residential_per_sqft": 15.50,
        "transit_levy_per_unit": 3500,
        "source": "City of Ottawa Development Charges By-law",
    }

    await set_cached(cache_key, schedule, ttl=604800)
    return schedule


async def aggregate_property_data(
    address: str | None = None,
    parcel_id: str | None = None,
) -> dict | None:
    """Aggregate all available data for a property."""
    property_data = None

    if parcel_id:
        property_data = await fetch_property_by_parcel_id(parcel_id)
    if not property_data and address:
        property_data = await fetch_property_by_address(address)

    if not property_data:
        return None

    pid = property_data.get("parcel_id", parcel_id or "")

    # Fetch additional data
    geo_data = await fetch_geo_ottawa_data(pid)

    # Combine
    combined = {
        "parcel_id": pid,
        "address": property_data.get("address", address),
        "city": "Ottawa",
        "province": "Ontario",
        "lot_width_ft": property_data.get("lot_width"),
        "lot_depth_ft": property_data.get("lot_depth"),
        "lot_area_sqft": property_data.get("lot_area"),
        "current_use": property_data.get("current_use"),
        "structure_type": property_data.get("structure_type"),
        "year_built": property_data.get("year_built"),
        "assessed_value": property_data.get("assessed_value"),
        "assessed_land_value": property_data.get("land_value"),
        "zoning_code": property_data.get("zoning"),
        "ward": property_data.get("ward"),
        "neighbourhood": property_data.get("neighbourhood"),
        "is_heritage": (geo_data or {}).get("heritage", {}).get("found", False),
        "is_floodplain": (geo_data or {}).get("floodplain", {}).get("found", False),
        "has_easements": (geo_data or {}).get("easements", {}).get("found", False),
        "raw_data": {
            "property": property_data,
            "geo": geo_data,
        },
    }

    return combined
