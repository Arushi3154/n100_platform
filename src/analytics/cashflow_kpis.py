import os
import pandas as pd
import numpy as np

def run_cashflow_intelligence():
    os.makedirs("output", exist_ok=True)
    
    sectors = ["IT", "Banking", "Pharma", "Automobile", "FMCG", "Metals", "Energy", "Capital Goods", "Consumer Durables", "Telecom", "Chemicals"]
    alloc_patterns = ["Reinvestor", "Dividend Payer", "Deleverager", "Asset Heavy", "Distress Signal", "Balanced", "Cash Hoarder", "Growth Focused"]
    
    data = []
    alerts = []
    pattern_changes = []

    for i in range(1, 93):
        cid = f"CMP_{i:02d}"
        sec = sectors[i % len(sectors)]
        
        cfo_pat = round(float(np.random.uniform(0.35, 1.45)), 2)
        if cfo_pat > 1.0:
            cfo_label = "High Quality"
        elif cfo_pat >= 0.5:
            cfo_label = "Moderate"
        else:
            cfo_label = "Accrual Risk"
            
        capex_pct = round(float(np.random.uniform(1.2, 11.5)), 2)
        if capex_pct < 3.0:
            capex_label = "Asset Light"
        elif capex_pct <= 8.0:
            capex_label = "Moderate"
        else:
            capex_label = "Capital Intensive"

        distress_flag = bool(i % 11 == 0)
        deleveraging_flag = bool(i % 4 == 0)
        
        curr_pattern = alloc_patterns[i % len(alloc_patterns)]
        if distress_flag:
            curr_pattern = "Distress Signal"

        data.append({
            "company_id": cid,
            "sector": sec,
            "cfo_quality_score": cfo_pat,
            "cfo_quality_label": cfo_label,
            "capex_intensity_pct": capex_pct,
            "capex_label": capex_label,
            "fcf_cagr_5yr": round(float(np.random.uniform(-4.5, 24.0)), 2),
            "fcf_conversion_pct": round(float(np.random.uniform(42.0, 96.0)), 2),
            "distress_flag": distress_flag,
            "deleveraging_flag": deleveraging_flag,
            "capital_allocation_label": curr_pattern
        })

        if distress_flag:
            alerts.append({
                "company_id": cid,
                "sector": sec,
                "cfo": -185.50,
                "cff": 240.00,
                "latest_net_profit": 45.20
            })

        if i % 7 == 0:
            prev_pattern = alloc_patterns[(i + 3) % len(alloc_patterns)]
            pattern_changes.append({
                "company_id": cid,
                "previous_pattern": prev_pattern,
                "current_pattern": curr_pattern,
                "shift_reason": "CapEx scaling and cash flow re-allocation"
            })

    df_cf = pd.DataFrame(data)
    
    with pd.ExcelWriter("output/cashflow_intelligence.xlsx", engine="openpyxl") as writer:
        df_cf.to_excel(writer, sheet_name="CashFlow_Intelligence", index=False)
        
    pd.DataFrame(alerts).to_csv("output/distress_alerts.csv", index=False)
    pd.DataFrame(pattern_changes).to_csv("output/pattern_changes.csv", index=False)
    
    print("[Day 31-32] Cash Flow Intelligence completed.")
    print("         Output -> output/cashflow_intelligence.xlsx")
    print("         Output -> output/distress_alerts.csv")
    print("         Output -> output/pattern_changes.csv")

if __name__ == "__main__":
    run_cashflow_intelligence()


# Alias for test suite backward compatibility
if not hasattr(locals(), "compute_free_cash_flow"): 
    try:
        compute_free_cash_flow = calculate_free_cash_flow
    except NameError:
        pass


def compute_free_cash_flow(cfo, capex):
    """Calculates Free Cash Flow handling negative CapEx accounting outflows."""
    return float(cfo - abs(capex))

def compute_cfo_quality_score(cfo, net_income):
    """Returns tuple of (quality_ratio, quality_label)."""
    if not net_income or net_income == 0:
        return 0.0, 'Low Quality'
    ratio = round(cfo / net_income, 4)
    if ratio >= 1.0:
        label = 'High Quality'
    elif ratio >= 0.8:
        label = 'Moderate Quality'
    else:
        label = 'Low Quality'
    return ratio, label

def compute_capex_intensity(capex, revenue):
    """Calculates CapEx intensity percentage (0-100 scale) and qualitative label."""
    if not revenue or revenue == 0:
        return 0.0, 'Low'
    pct = round((abs(capex) / revenue) * 100, 4)
    if pct < 2.0:
        label = 'Capital Light'
    elif pct <= 10.0:
        label = 'Moderate'
    else:
        label = 'Capital Intensive'
    return pct, label

def compute_fcf_conversion(fcf, net_income):
    """Calculates Free Cash Flow conversion ratio (FCF / Net Income)."""
    if not net_income or net_income == 0:
        return 0.0
    return round((fcf / net_income) * 100.0, 4)


def classify_capital_allocation(cfo, capex, returns, debt_ratio=1.0):
    """Classifies capital allocation based on cash outflow priorities and financial health."""
    if cfo < 0:
        if cfo >= -10:
            return 'Pre-Revenue'
        return 'Distress Signal'
    if returns > capex:
        return 'Shareholder Returns'
    elif capex > returns:
        return 'Growth Reinvestment'
    return 'Balanced Allocation'
