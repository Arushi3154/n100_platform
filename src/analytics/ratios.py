import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

def compute_profitability_ratios(
    net_profit: float,
    sales: float,
    operating_profit: float,
    opm_percentage: Optional[float],
    ebit: float,
    equity_capital: float,
    reserves: float,
    borrowings: float,
    total_assets: float,
    broad_sector: str
) -> Dict[str, Optional[float]]:
    npm = (net_profit / sales * 100) if sales and sales > 0 else None
    
    opm = (operating_profit / sales * 100) if sales and sales > 0 else None
    if opm is not None and opm_percentage is not None:
        if abs(opm - opm_percentage) > 1.0:
            logger.warning(f"OPM Mismatch > 1%: Computed={opm:.2f}%, Expected={opm_percentage:.2f}%")

    total_equity = equity_capital + reserves
    roe = (net_profit / total_equity * 100) if total_equity > 0 else None

    capital_employed = total_equity + borrowings
    roce = (ebit / capital_employed * 100) if capital_employed > 0 else None

    roa = (net_profit / total_assets * 100) if total_assets and total_assets > 0 else None

    return {
        "net_profit_margin_pct": round(npm, 2) if npm else None,
        "operating_profit_margin_pct": round(opm, 2) if opm else None,
        "return_on_equity_pct": round(roe, 2) if roe else None,
        "return_on_capital_employed_pct": round(roce, 2) if roce else None,
        "return_on_assets_pct": round(roa, 2) if roa else None
    }

def compute_leverage_efficiency_ratios(
    borrowings: float,
    equity_capital: float,
    reserves: float,
    operating_profit: float,
    other_income: float,
    interest: float,
    investments: float,
    sales: float,
    total_assets: float,
    broad_sector: str
) -> Dict[str, Any]:
    total_equity = equity_capital + reserves
    
    if borrowings == 0:
        de_ratio = 0.0
    elif total_equity <= 0:
        de_ratio = None
    else:
        de_ratio = round(borrowings / total_equity, 2)

    is_financial = broad_sector.upper() in ["FINANCIALS", "FINANCIAL SERVICES", "BANKS", "NBFC"]
    high_leverage_flag = bool(de_ratio and de_ratio > 5.0 and not is_financial)

    icr_label = None
    if interest == 0 or interest is None:
        icr = None
        icr_label = "Debt Free"
    else:
        icr = round((operating_profit + (other_income or 0.0)) / interest, 2)

    icr_warning_flag = bool(icr is not None and icr < 1.5)
    net_debt = borrowings - (investments or 0.0)
    asset_turnover = round(sales / total_assets, 2) if total_assets and total_assets > 0 else None

    return {
        "debt_to_equity": de_ratio,
        "high_leverage_flag": high_leverage_flag,
        "interest_coverage": icr,
        "icr_label": icr_label,
        "icr_warning_flag": icr_warning_flag,
        "net_debt_cr": round(net_debt, 2),
        "asset_turnover": asset_turnover
    }
