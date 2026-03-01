"""Tests for the Ottawa zoning parser."""

from app.services.zoning_parser import (
    ZoneCategory,
    calculate_development_potential,
    get_zoning_envelope,
    map_zone_to_development_types,
    parse_zone_code,
)


def test_parse_zone_code_basic():
    base, suffix = parse_zone_code("R4")
    assert base == "R4"
    assert suffix is None


def test_parse_zone_code_with_suffix():
    base, suffix = parse_zone_code("R4[2.0] H(14.5)")
    assert base == "R4"
    assert suffix == "[2.0] H(14.5)"


def test_get_zoning_envelope_r4():
    envelope = get_zoning_envelope("R4")
    assert envelope is not None
    assert envelope.zone_code == "R4"
    assert envelope.zone_category == ZoneCategory.RESIDENTIAL
    assert envelope.max_height_m == 14.5
    assert envelope.max_storeys == 4
    assert envelope.max_fsi == 1.5
    assert "low_rise_apartment" in envelope.permitted_uses


def test_get_zoning_envelope_with_height_override():
    envelope = get_zoning_envelope("R4 H(11.0)")
    assert envelope is not None
    assert envelope.max_height_m == 11.0


def test_get_zoning_envelope_with_fsi_override():
    envelope = get_zoning_envelope("R4[2.0]")
    assert envelope is not None
    assert envelope.max_fsi == 2.0


def test_get_zoning_envelope_unknown():
    envelope = get_zoning_envelope("ZZ99")
    assert envelope is None


def test_calculate_development_potential_r4():
    envelope = get_zoning_envelope("R4")
    assert envelope is not None

    potential = calculate_development_potential(
        envelope,
        lot_area_sqft=6000.0,
        lot_width_ft=50.0,
        lot_depth_ft=120.0,
    )

    assert potential["zone_code"] == "R4"
    assert potential["zone_category"] == "residential"
    assert "max_gfa_sqft" in potential
    assert potential["max_gfa_sqft"] > 0
    assert "max_units" in potential
    assert potential["max_units"] >= 1
    assert potential["max_height_m"] == 14.5
    assert potential["max_storeys"] == 4


def test_calculate_development_potential_r1():
    envelope = get_zoning_envelope("R1")
    assert envelope is not None

    potential = calculate_development_potential(
        envelope,
        lot_area_sqft=8000.0,
        lot_width_ft=60.0,
        lot_depth_ft=133.0,
    )

    assert potential["zone_code"] == "R1"
    assert "detached_dwelling" in potential["permitted_uses"]


def test_map_zone_to_development_types_r4():
    types = map_zone_to_development_types("R4")
    assert "multi_unit_apartment" in types
    assert "single_family_replacement" in types


def test_map_zone_to_development_types_gm():
    types = map_zone_to_development_types("GM")
    assert "commercial_development" in types
    assert "mixed_use_development" in types


def test_map_zone_to_development_types_unknown():
    types = map_zone_to_development_types("ZZ99")
    assert types == ["unknown"]
