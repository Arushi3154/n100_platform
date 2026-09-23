from typing import Tuple, Optional

def compute_cagr(start_val: Optional[float], end_val: Optional[float], n_years: int) -> Tuple[Optional[float], str]:
    if start_val is None or end_val is None or n_years is None or n_years <= 0:
        return None, "INSUFFICIENT"
    if start_val == 0:
        return None, "ZERO_BASE"
    if start_val > 0 and end_val > 0:
        cagr_val = ((end_val / start_val) ** (1.0 / n_years) - 1.0) * 100.0
        return round(cagr_val, 2), "NORMAL"
    if start_val > 0 and end_val < 0:
        return None, "DECLINE_TO_LOSS"
    if start_val < 0 and end_val > 0:
        return None, "TURNAROUND"
    if start_val < 0 and end_val < 0:
        return None, "BOTH_NEGATIVE"
    return None, "INSUFFICIENT"
