"""
Zoning Parser for Ottawa By-law 2008-250.

Extracts development rights, permitted uses, building envelope constraints,
and maps zoning codes to development potential.
"""

import re
from dataclasses import dataclass, field
from enum import Enum

import httpx

from app.core.cache import get_cached, set_cached
from app.core.config import settings


class ZoneCategory(str, Enum):
    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"
    MIXED_USE = "mixed_use"
    INDUSTRIAL = "industrial"
    INSTITUTIONAL = "institutional"
    RURAL = "rural"
    OPEN_SPACE = "open_space"


@dataclass
class ZoningEnvelope:
    """Building envelope constraints from Ottawa zoning by-law."""
    zone_code: str
    zone_category: ZoneCategory
    zone_suffix: str | None = None
    bylaw_reference: str = "2008-250"

    # Permitted uses
    permitted_uses: list[str] = field(default_factory=list)
    conditional_uses: list[str] = field(default_factory=list)

    # Building envelope
    max_height_m: float | None = None
    max_storeys: int | None = None
    max_fsi: float | None = None
    max_lot_coverage_pct: float | None = None
    max_density_units_per_ha: float | None = None

    # Setbacks (metres)
    front_setback_m: float | None = None
    rear_setback_m: float | None = None
    interior_side_setback_m: float | None = None
    exterior_side_setback_m: float | None = None

    # Parking
    min_parking_spaces_per_unit: float | None = None
    min_bicycle_parking_per_unit: float | None = None

    # Amenity
    min_amenity_area_sqm_per_unit: float | None = None
    min_landscaped_area_pct: float | None = None

    # Overlays / exceptions
    overlays: list[str] = field(default_factory=list)
    exceptions: list[str] = field(default_factory=list)
    secondary_plan: str | None = None

    # Source
    source_text: str | None = None


# Ottawa Zoning By-law 2008-250 reference data
# Extracted from the official by-law provisions
ZONING_DEFINITIONS: dict[str, ZoningEnvelope] = {
    "R1": ZoningEnvelope(
        zone_code="R1",
        zone_category=ZoneCategory.RESIDENTIAL,
        permitted_uses=["detached_dwelling"],
        conditional_uses=["home_based_business", "secondary_dwelling_unit", "group_home"],
        max_height_m=11.0,
        max_storeys=3,
        max_lot_coverage_pct=35.0,
        front_setback_m=6.0,
        rear_setback_m=7.5,
        interior_side_setback_m=1.5,
        exterior_side_setback_m=4.5,
        min_parking_spaces_per_unit=1.0,
    ),
    "R2": ZoningEnvelope(
        zone_code="R2",
        zone_category=ZoneCategory.RESIDENTIAL,
        permitted_uses=["detached_dwelling", "semi_detached_dwelling", "duplex"],
        conditional_uses=["home_based_business", "secondary_dwelling_unit", "group_home"],
        max_height_m=11.0,
        max_storeys=3,
        max_lot_coverage_pct=40.0,
        front_setback_m=5.5,
        rear_setback_m=7.5,
        interior_side_setback_m=1.2,
        exterior_side_setback_m=4.5,
        min_parking_spaces_per_unit=1.0,
    ),
    "R3": ZoningEnvelope(
        zone_code="R3",
        zone_category=ZoneCategory.RESIDENTIAL,
        permitted_uses=[
            "detached_dwelling", "semi_detached_dwelling", "duplex",
            "townhouse", "three_unit_dwelling",
        ],
        conditional_uses=[
            "home_based_business", "secondary_dwelling_unit", "group_home",
            "bed_and_breakfast",
        ],
        max_height_m=11.0,
        max_storeys=3,
        max_lot_coverage_pct=45.0,
        max_density_units_per_ha=60.0,
        front_setback_m=4.5,
        rear_setback_m=7.5,
        interior_side_setback_m=1.2,
        exterior_side_setback_m=4.5,
        min_parking_spaces_per_unit=1.0,
    ),
    "R4": ZoningEnvelope(
        zone_code="R4",
        zone_category=ZoneCategory.RESIDENTIAL,
        permitted_uses=[
            "detached_dwelling", "semi_detached_dwelling", "duplex",
            "townhouse", "three_unit_dwelling", "four_unit_dwelling",
            "low_rise_apartment", "stacked_dwelling",
        ],
        conditional_uses=[
            "home_based_business", "group_home", "bed_and_breakfast",
            "rooming_house", "shelter",
        ],
        max_height_m=14.5,
        max_storeys=4,
        max_fsi=1.5,
        max_lot_coverage_pct=50.0,
        max_density_units_per_ha=120.0,
        front_setback_m=3.0,
        rear_setback_m=7.5,
        interior_side_setback_m=1.2,
        exterior_side_setback_m=3.0,
        min_parking_spaces_per_unit=0.5,
        min_amenity_area_sqm_per_unit=6.0,
    ),
    "R5": ZoningEnvelope(
        zone_code="R5",
        zone_category=ZoneCategory.RESIDENTIAL,
        permitted_uses=[
            "detached_dwelling", "semi_detached_dwelling", "duplex",
            "townhouse", "low_rise_apartment", "mid_rise_apartment",
            "stacked_dwelling",
        ],
        conditional_uses=[
            "group_home", "rooming_house", "shelter",
            "retirement_home", "diplomatic_mission",
        ],
        max_height_m=20.0,
        max_storeys=6,
        max_fsi=2.0,
        max_lot_coverage_pct=55.0,
        max_density_units_per_ha=200.0,
        front_setback_m=3.0,
        rear_setback_m=7.5,
        interior_side_setback_m=1.5,
        exterior_side_setback_m=3.0,
        min_parking_spaces_per_unit=0.5,
        min_amenity_area_sqm_per_unit=6.0,
    ),
    "GM": ZoningEnvelope(
        zone_code="GM",
        zone_category=ZoneCategory.MIXED_USE,
        permitted_uses=[
            "retail_store", "restaurant", "office", "personal_service",
            "dwelling_unit_above_ground_floor", "medical_facility",
            "community_centre", "daycare",
        ],
        conditional_uses=[
            "gas_station", "drive_through", "place_of_worship",
            "parking_garage",
        ],
        max_height_m=20.0,
        max_storeys=6,
        max_fsi=2.0,
        max_lot_coverage_pct=70.0,
        front_setback_m=0.0,
        rear_setback_m=7.5,
        interior_side_setback_m=0.0,
        exterior_side_setback_m=0.0,
        min_parking_spaces_per_unit=0.25,
    ),
    "TM": ZoningEnvelope(
        zone_code="TM",
        zone_category=ZoneCategory.MIXED_USE,
        permitted_uses=[
            "retail_store", "restaurant", "office", "personal_service",
            "dwelling_unit", "hotel", "entertainment", "medical_facility",
        ],
        conditional_uses=["parking_garage", "gas_station"],
        max_height_m=30.0,
        max_storeys=9,
        max_fsi=3.0,
        max_lot_coverage_pct=80.0,
        front_setback_m=0.0,
        rear_setback_m=7.5,
        interior_side_setback_m=0.0,
        exterior_side_setback_m=0.0,
        min_parking_spaces_per_unit=0.2,
    ),
    "MC": ZoningEnvelope(
        zone_code="MC",
        zone_category=ZoneCategory.MIXED_USE,
        permitted_uses=[
            "retail_store", "restaurant", "office", "personal_service",
            "dwelling_unit", "hotel", "entertainment", "community_centre",
            "high_rise_apartment",
        ],
        conditional_uses=["parking_garage"],
        max_height_m=None,  # Per site-specific schedule
        max_storeys=None,
        max_fsi=5.0,
        max_lot_coverage_pct=90.0,
        front_setback_m=0.0,
        rear_setback_m=0.0,
        interior_side_setback_m=0.0,
        exterior_side_setback_m=0.0,
        min_parking_spaces_per_unit=0.2,
    ),
    "LC": ZoningEnvelope(
        zone_code="LC",
        zone_category=ZoneCategory.COMMERCIAL,
        permitted_uses=[
            "retail_store", "restaurant", "office", "personal_service",
            "medical_facility", "daycare",
        ],
        conditional_uses=["gas_station", "drive_through", "car_wash"],
        max_height_m=11.0,
        max_storeys=2,
        max_lot_coverage_pct=40.0,
        front_setback_m=3.0,
        rear_setback_m=6.0,
        interior_side_setback_m=3.0,
        exterior_side_setback_m=3.0,
        min_parking_spaces_per_unit=1.0,
    ),
    "AM": ZoningEnvelope(
        zone_code="AM",
        zone_category=ZoneCategory.MIXED_USE,
        permitted_uses=[
            "retail_store", "restaurant", "office", "personal_service",
            "dwelling_unit", "hotel", "entertainment", "light_industrial",
        ],
        conditional_uses=["parking_garage", "gas_station"],
        max_height_m=30.0,
        max_storeys=9,
        max_fsi=3.0,
        max_lot_coverage_pct=80.0,
        front_setback_m=0.0,
        rear_setback_m=7.5,
        interior_side_setback_m=0.0,
        exterior_side_setback_m=0.0,
        min_parking_spaces_per_unit=0.2,
    ),
}


def parse_zone_code(raw_code: str) -> tuple[str, str | None]:
    """Parse a zone code like 'R4[2.0] H(14.5)' into base code and suffix."""
    match = re.match(r"^([A-Z]{1,3}\d?)", raw_code.strip().upper())
    if not match:
        return raw_code.strip().upper(), None
    base = match.group(1)
    suffix = raw_code[match.end():].strip() or None
    return base, suffix


def get_zoning_envelope(zone_code: str) -> ZoningEnvelope | None:
    """Look up the zoning envelope for a given zone code."""
    base_code, suffix = parse_zone_code(zone_code)
    envelope = ZONING_DEFINITIONS.get(base_code)
    if envelope is None:
        return None

    # Apply suffix overrides (e.g., height/FSI modifiers)
    if suffix:
        envelope.zone_suffix = suffix
        height_match = re.search(r"H\((\d+\.?\d*)\)", suffix)
        if height_match:
            envelope.max_height_m = float(height_match.group(1))
        fsi_match = re.search(r"\[(\d+\.?\d*)\]", suffix)
        if fsi_match:
            envelope.max_fsi = float(fsi_match.group(1))

    return envelope


def calculate_development_potential(
    envelope: ZoningEnvelope,
    lot_area_sqft: float,
    lot_width_ft: float | None = None,
    lot_depth_ft: float | None = None,
) -> dict:
    """Calculate development potential given zoning rules and lot dimensions."""
    lot_area_sqm = lot_area_sqft * 0.092903

    result = {
        "zone_code": envelope.zone_code,
        "zone_category": envelope.zone_category.value,
        "permitted_uses": envelope.permitted_uses,
        "conditional_uses": envelope.conditional_uses,
    }

    # Maximum buildable area based on FSI
    if envelope.max_fsi:
        max_gfa_sqm = lot_area_sqm * envelope.max_fsi
        max_gfa_sqft = max_gfa_sqm / 0.092903
        result["max_gfa_sqft"] = round(max_gfa_sqft, 0)
        result["max_gfa_sqm"] = round(max_gfa_sqm, 0)
    elif envelope.max_lot_coverage_pct and envelope.max_storeys:
        footprint_sqm = lot_area_sqm * (envelope.max_lot_coverage_pct / 100)
        max_gfa_sqm = footprint_sqm * envelope.max_storeys
        max_gfa_sqft = max_gfa_sqm / 0.092903
        result["max_gfa_sqft"] = round(max_gfa_sqft, 0)
        result["max_gfa_sqm"] = round(max_gfa_sqm, 0)

    # Maximum footprint based on lot coverage
    if envelope.max_lot_coverage_pct:
        max_footprint_sqm = lot_area_sqm * (envelope.max_lot_coverage_pct / 100)
        result["max_footprint_sqft"] = round(max_footprint_sqm / 0.092903, 0)

    # Calculate buildable envelope considering setbacks
    if lot_width_ft and lot_depth_ft:
        width_m = lot_width_ft * 0.3048
        depth_m = lot_depth_ft * 0.3048

        buildable_width = width_m
        buildable_depth = depth_m
        if envelope.interior_side_setback_m:
            buildable_width -= 2 * envelope.interior_side_setback_m
        if envelope.front_setback_m:
            buildable_depth -= envelope.front_setback_m
        if envelope.rear_setback_m:
            buildable_depth -= envelope.rear_setback_m

        if buildable_width > 0 and buildable_depth > 0:
            buildable_area_sqm = buildable_width * buildable_depth
            result["buildable_envelope_sqft"] = round(buildable_area_sqm / 0.092903, 0)
            result["buildable_width_m"] = round(buildable_width, 1)
            result["buildable_depth_m"] = round(buildable_depth, 1)

    # Maximum units based on density
    if envelope.max_density_units_per_ha:
        lot_ha = lot_area_sqm / 10000
        max_units = int(lot_ha * envelope.max_density_units_per_ha)
        result["max_units_by_density"] = max(max_units, 1)

    # Estimate max units from GFA (assuming ~75 sqm per unit average)
    if "max_gfa_sqm" in result:
        avg_unit_sqm = 75.0
        max_units_by_gfa = int(result["max_gfa_sqm"] / avg_unit_sqm)
        result["max_units_by_gfa"] = max(max_units_by_gfa, 1)

        # Take the lesser of density and GFA limits
        if "max_units_by_density" in result:
            result["max_units"] = min(result["max_units_by_density"], result["max_units_by_gfa"])
        else:
            result["max_units"] = result["max_units_by_gfa"]

    # Building envelope summary
    result["max_height_m"] = envelope.max_height_m
    result["max_storeys"] = envelope.max_storeys
    result["max_fsi"] = envelope.max_fsi
    result["max_lot_coverage_pct"] = envelope.max_lot_coverage_pct
    result["setbacks"] = {
        "front_m": envelope.front_setback_m,
        "rear_m": envelope.rear_setback_m,
        "interior_side_m": envelope.interior_side_setback_m,
        "exterior_side_m": envelope.exterior_side_setback_m,
    }

    # Parking requirements
    if envelope.min_parking_spaces_per_unit and "max_units" in result:
        result["min_parking_spaces"] = int(
            result["max_units"] * envelope.min_parking_spaces_per_unit + 0.99
        )

    return result


async def fetch_zoning_from_open_data(parcel_id: str) -> dict | None:
    """Fetch zoning data from Ottawa Open Data API."""
    cache_key = f"zoning:{parcel_id}"
    cached = await get_cached(cache_key)
    if cached:
        return cached

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{settings.ottawa_open_data_url}/records/1.0/search/",
                params={
                    "dataset": "zoning",
                    "q": parcel_id,
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


def map_zone_to_development_types(zone_code: str) -> list[str]:
    """Map a zoning code to potential development types for analysis."""
    base_code, _ = parse_zone_code(zone_code)
    envelope = ZONING_DEFINITIONS.get(base_code)
    if not envelope:
        return ["unknown"]

    development_types = []

    if envelope.zone_category == ZoneCategory.RESIDENTIAL:
        if "detached_dwelling" in envelope.permitted_uses:
            development_types.append("single_family_replacement")
        if any(u in envelope.permitted_uses for u in ["duplex", "semi_detached_dwelling"]):
            development_types.append("duplex_conversion")
        if any(u in envelope.permitted_uses for u in ["townhouse", "stacked_dwelling"]):
            development_types.append("townhouse_development")
        if any(u in envelope.permitted_uses for u in
               ["low_rise_apartment", "mid_rise_apartment", "four_unit_dwelling"]):
            development_types.append("multi_unit_apartment")
    elif envelope.zone_category in (ZoneCategory.MIXED_USE, ZoneCategory.COMMERCIAL):
        development_types.append("commercial_development")
        if "dwelling_unit" in envelope.permitted_uses or \
           "dwelling_unit_above_ground_floor" in envelope.permitted_uses:
            development_types.append("mixed_use_development")
        if "high_rise_apartment" in envelope.permitted_uses:
            development_types.append("high_rise_residential")

    return development_types or ["single_family_replacement"]
