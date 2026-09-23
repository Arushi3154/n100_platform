from typing import Dict, Any, Optional

def compute_free_cash_flow(operating_activity: float, investing_activity: float) -> float:
    return round(operating_activity + investing_activity, 2)

def compute_cfo_quality_score(cfo_5yr_avg: float, pat_5yr_avg: float) -> Tuple[Optional[float], Optional[str]]:
    if pat_5yr_avg == 0 or pat_5yr_avg is None or cfo_5yr_avg is None:
        return None, None
    ratio = round(cfo_5yr_avg / pat_5yr_avg, 2)
    if ratio > 1.0:
        label = "High Quality"
    elif 0.5 <= ratio <= 1.0:
        label = "Moderate"
    else:
        label = "Accrual Risk"
    return ratio, label

def compute_capex_intensity(investing_activity: float, sales: float) -> Tuple[Optional[float], Optional[str]]:
    if sales == 0 or sales is None or investing_activity is None:
        return None, None
    pct = round((abs(investing_activity) / sales) * 100.0, 2)
    if pct < 3.0:
        label = "Asset Light"
    elif 3.0 <= pct <= 8.0:
        label = "Moderate"
    else:
        label = "Capital Intensive"
    return pct, label

def compute_fcf_conversion(fcf: float, operating_profit: float) -> Optional[float]:
    if operating_profit == 0 or operating_profit is None or fcf is None:
        return None
    return round((fcf / operating_profit) * 100.0, 2)

def classify_capital_allocation(cfo: float, cfi: float, cff: float, cfo_pat_ratio: Optional[float] = None) -> str:
    s_cfo = "+" if cfo > 0 else "-"
    s_cfi = "+" if cfi > 0 else "-"
    s_cff = "+" if cff > 0 else "-"
    pattern = (s_cfo, s_cfi, s_cff)

    if pattern == ("+", "-", "-"):
        if cfo_pat_ratio and cfo_pat_ratio > 1.0:
            return "Shareholder Returns"
        return "Reinvestor"
    elif pattern == ("+", "+", "-"):
        return "Liquidating Assets"
    elif pattern == ("-", "+", "+"):
        return "Distress Signal"
    elif pattern == ("-", "-", "+"):
        return "Growth Funded by Debt"
    elif pattern == ("+", "+", "+"):
        return "Cash Accumulator"
    elif pattern == ("-", "-", "-"):
        return "Pre-Revenue"
    else:
        return "Mixed"
