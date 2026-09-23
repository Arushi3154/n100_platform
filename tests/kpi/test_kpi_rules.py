import pytest
from src.analytics.ratios import compute_profitability_ratios, compute_leverage_efficiency_ratios
from src.analytics.cagr import compute_cagr
from src.analytics.cashflow_kpis import (
    compute_free_cash_flow, compute_cfo_quality_score,
    compute_capex_intensity, compute_fcf_conversion, classify_capital_allocation
)

# Profitability Tests (8)
def test_profitability_normal():
    res = compute_profitability_ratios(10, 100, 20, 20.0, 15, 40, 10, 20, 200, "IT")
    assert res["net_profit_margin_pct"] == 10.0
    assert res["operating_profit_margin_pct"] == 20.0
    assert res["return_on_equity_pct"] == 20.0

def test_profitability_zero_sales():
    res = compute_profitability_ratios(10, 0, 20, None, 15, 40, 10, 20, 200, "IT")
    assert res["net_profit_margin_pct"] is None
    assert res["operating_profit_margin_pct"] is None

def test_profitability_negative_equity():
    res = compute_profitability_ratios(10, 100, 20, 20.0, 15, -50, 10, 20, 200, "IT")
    assert res["return_on_equity_pct"] is None

def test_profitability_financials_roce():
    res = compute_profitability_ratios(10, 100, 20, 20.0, 15, 40, 10, 20, 200, "FINANCIALS")
    assert res["return_on_capital_employed_pct"] is not None

def test_roa_normal():
    res = compute_profitability_ratios(10, 100, 20, 20.0, 15, 40, 10, 20, 200, "IT")
    assert res["return_on_assets_pct"] == 5.0

def test_roa_zero_assets():
    res = compute_profitability_ratios(10, 100, 20, 20.0, 15, 40, 10, 20, 0, "IT")
    assert res["return_on_assets_pct"] is None

def test_opm_mismatch_warning(caplog):
    compute_profitability_ratios(10, 100, 30, 20.0, 15, 40, 10, 20, 200, "IT")
    assert "OPM Mismatch > 1%" in caplog.text

def test_profitability_zero_capital_employed():
    res = compute_profitability_ratios(10, 100, 20, 20.0, 15, -10, 0, 0, 200, "IT")
    assert res["return_on_capital_employed_pct"] is None

# Leverage & Efficiency Tests (4)
def test_de_debt_free():
    res = compute_leverage_efficiency_ratios(0, 50, 50, 20, 5, 0, 10, 100, 200, "IT")
    assert res["debt_to_equity"] == 0.0
    assert res["interest_coverage"] is None
    assert res["icr_label"] == "Debt Free"

def test_icr_warning_and_high_de():
    res = compute_leverage_efficiency_ratios(600, 10, 10, 10, 0, 20, 0, 100, 200, "INDUSTRIAL")
    assert res["high_leverage_flag"] is True
    assert res["icr_warning_flag"] is True

def test_financials_high_de_suppressed():
    res = compute_leverage_efficiency_ratios(600, 10, 10, 10, 0, 20, 0, 100, 200, "FINANCIALS")
    assert res["high_leverage_flag"] is False

def test_net_debt_and_asset_turnover():
    res = compute_leverage_efficiency_ratios(100, 50, 50, 20, 5, 10, 30, 200, 100, "IT")
    assert res["net_debt_cr"] == 70.0
    assert res["asset_turnover"] == 2.0

# CAGR Engine Tests (5)
def test_cagr_normal():
    val, flag = compute_cagr(100, 133.1, 3)
    assert val == 10.0
    assert flag == "NORMAL"

def test_cagr_turnaround():
    val, flag = compute_cagr(-50, 100, 5)
    assert val is None
    assert flag == "TURNAROUND"

def test_cagr_decline_to_loss():
    val, flag = compute_cagr(100, -20, 5)
    assert val is None
    assert flag == "DECLINE_TO_LOSS"

def test_cagr_both_negative():
    val, flag = compute_cagr(-10, -50, 3)
    assert val is None
    assert flag == "BOTH_NEGATIVE"

def test_cagr_zero_base():
    val, flag = compute_cagr(0, 100, 3)
    assert val is None
    assert flag == "ZERO_BASE"

# Cash Flow & Allocation Classifier Tests (3)
def test_cashflow_metrics():
    assert compute_free_cash_flow(100, -40) == 60.0
    q_ratio, q_label = compute_cfo_quality_score(120, 100)
    assert q_ratio == 1.2
    assert q_label == "High Quality"

def test_capex_intensity_and_fcf_conversion():
    pct, label = compute_capex_intensity(-5, 100)
    assert pct == 5.0
    assert label == "Moderate"
    assert compute_fcf_conversion(50, 100) == 50.0

def test_capital_allocation_classifiers():
    assert classify_capital_allocation(100, -30, -20, 1.2) == "Shareholder Returns"
    assert classify_capital_allocation(-50, 20, 20) == "Distress Signal"
    assert classify_capital_allocation(-10, -10, -10) == "Pre-Revenue"
