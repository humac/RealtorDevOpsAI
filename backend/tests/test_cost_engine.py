"""Tests for the Ottawa cost estimation engine."""

from app.services.ottawa_cost_engine import (
    ConstructionType,
    DevelopmentType,
    calculate_roi_metrics,
    estimate_construction_cost,
    estimate_financing_cost,
    estimate_hst,
    estimate_revenue,
    estimate_soft_costs,
    estimate_teardown_cost,
    generate_full_cost_estimate,
    run_sensitivity_analysis,
)


def test_estimate_construction_cost_woodframe():
    result = estimate_construction_cost(5000, ConstructionType.WOODFRAME, "mid")
    assert result["total"] == 5000 * 275.0
    assert result["construction_type"] == "woodframe"


def test_estimate_construction_cost_concrete():
    result = estimate_construction_cost(5000, ConstructionType.CONCRETE, "mid")
    assert result["total"] == 5000 * 400.0


def test_estimate_teardown_cost_basic():
    result = estimate_teardown_cost(1500, quality="mid")
    assert result["total"] == 22500.0
    assert result["hazmat_cost"] == 0


def test_estimate_teardown_cost_with_hazmat():
    result = estimate_teardown_cost(1500, hazmat=["asbestos", "lead"], quality="mid")
    assert result["hazmat_cost"] == 8000.0
    assert result["total"] > 22500.0


def test_estimate_teardown_cost_large_structure():
    result = estimate_teardown_cost(4000, quality="mid")
    assert result["total"] > 22500.0  # scaled up for larger structure


def test_estimate_soft_costs():
    result = estimate_soft_costs(
        hard_construction_cost=1000000,
        development_type=DevelopmentType.LOW_RISE_APARTMENT,
        num_units=6,
        gfa_sqft=5000,
        requires_site_plan=True,
        quality="mid",
    )
    assert result["architect"] == 100000.0
    assert result["development_charges"] == 22500.0 * 6
    assert result["total"] > 0


def test_estimate_financing_cost():
    result = estimate_financing_cost(
        total_project_cost=2000000,
        construction_months=18,
        down_payment_pct=0.25,
    )
    assert result["loan_amount"] == 1500000.0
    assert result["interest_cost"] > 0
    assert result["total"] > result["interest_cost"]


def test_estimate_hst_new_construction():
    result = estimate_hst(400000, 1, is_new_construction=True)
    assert result["gross_hst"] == 400000 * 0.13
    assert result["rebate"] > 0
    assert result["net_hst"] < result["gross_hst"]


def test_estimate_hst_resale():
    result = estimate_hst(400000, 1, is_new_construction=False)
    assert result["total"] == 0


def test_estimate_revenue_sale():
    result = estimate_revenue(DevelopmentType.LOW_RISE_APARTMENT, 5000, 6, "mid")
    assert "total_sale_revenue" in result
    assert result["total_sale_revenue"] == 5000 * 400.0


def test_estimate_revenue_rental():
    result = estimate_revenue(DevelopmentType.LOW_RISE_APARTMENT, 5000, 6, "mid", is_rental=True)
    assert "effective_annual_rental" in result
    assert "net_operating_income" in result


def test_calculate_roi_metrics_sale():
    metrics = calculate_roi_metrics(
        total_cost=2000000,
        sale_revenue=3000000,
        equity_invested=500000,
    )
    assert metrics["profit"] == 1000000.0
    assert metrics["roi_pct"] == 50.0
    assert metrics["profit_margin_pct"] > 0


def test_calculate_roi_metrics_rental():
    metrics = calculate_roi_metrics(
        total_cost=2000000,
        annual_noi=150000,
        equity_invested=500000,
    )
    assert metrics["cap_rate_pct"] == 7.5
    assert "cash_on_cash_pct" in metrics


def test_run_sensitivity_analysis():
    results = run_sensitivity_analysis(
        base_costs={"hard_construction": 1000000, "soft_costs": 300000, "financing": 100000},
        base_revenue=2000000,
        num_simulations=100,
    )
    assert len(results) == 4
    assert all("variable" in r for r in results)
    assert all("impact_on_roi_pct" in r for r in results)


def test_generate_full_cost_estimate():
    result = generate_full_cost_estimate(
        acquisition_cost=850000,
        gfa_sqft=5000,
        num_units=6,
        development_type=DevelopmentType.LOW_RISE_APARTMENT,
        construction_type=ConstructionType.WOODFRAME,
        construction_months=18,
        existing_gfa_sqft=1500,
        requires_teardown=True,
        requires_site_plan=True,
    )
    assert result["acquisition_cost"] == 850000
    assert result["total_cost"] > 850000
    assert "roi_metrics" in result
    assert "sensitivity_analysis" in result
    assert len(result["sensitivity_analysis"]) > 0
