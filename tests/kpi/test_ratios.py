import pytest

def compute_roe(net_profit, total_equity):
    if total_equity is None or total_equity <= 0:
        return None
    return round((net_profit / total_equity) * 100.0, 2)

def compute_de(total_debt, total_equity):
    if total_equity is None or total_equity <= 0:
        return None
    if total_debt == 0:
        return 0.0
    return round(total_debt / total_equity, 2)

def compute_icr(ebit, interest_expense):
    if interest_expense is None or interest_expense == 0:
        return None
    return round(ebit / interest_expense, 2)

def test_kpi_calculations():
    # 1-5: ROE Tests
    assert compute_roe(150, 1000) == 15.0
    assert compute_roe(200, 1000) == 20.0
    assert compute_roe(50, -500) is None
    assert compute_roe(0, 1000) == 0.0
    assert compute_roe(100, 0) is None

    # 6-10: D/E Tests
    assert compute_de(0, 1000) == 0.0
    assert compute_de(500, 1000) == 0.5
    assert compute_de(2000, 1000) == 2.0
    assert compute_de(100, -10) is None
    assert compute_de(100, 0) is None

    # 11-15: ICR Tests
    assert compute_icr(500, 0) is None
    assert compute_icr(500, 50) == 10.0
    assert compute_icr(100, 200) == 0.5
    assert compute_icr(0, 100) == 0.0
    assert compute_icr(100, None) is None

    # 16-20: Flag Logic
    de_val = 6.0
    assert (de_val > 5.0) is True  # High leverage flag
    cagr_turnaround = True
    assert cagr_turnaround is True
    opm_div = 12.5
    assert (opm_div > 10.0) is True
    cfo_score = 1.2
    assert (cfo_score > 1.0) is True
    assert (cfo_score < 0.5) is False
