import os
import sqlite3
import pandas as pd
import numpy as np
from src.screener.engine import load_screener_config, run_screener_preset, export_screener_excel
from src.analytics.peer import compute_peer_percentiles
from src.analytics.radar import generate_radar_charts
from src.analytics.export_peer_excel import export_peer_comparison_excel

SECTORS = [
    "IT Services", "Financial Services", "FMCG", "Pharma", "Automobile", 
    "Capital Goods", "Metals", "Oil & Gas", "Power", "Telecom", "Consumer Durables"
]

def generate_synthetic_universe(num_companies: int = 100, year: int = 2024):
    """Generates a synthetic universe of NIFTY 100 companies and peer group mappings."""
    np.random.seed(42)
    company_ids = [f"COMP_{i:03d}" for i in range(1, num_companies + 1)]
    sectors = [np.random.choice(SECTORS) for _ in range(num_companies)]
    
    data = {
        "company_id": company_ids,
        "company_name": [f"Company {i}" for i in range(1, num_companies + 1)],
        "broad_sector": sectors,
        "market_cap_cr": np.random.uniform(10000, 500000, num_companies).round(2),
        "sales_cr": np.random.uniform(1000, 100000, num_companies).round(2),
        "return_on_equity_pct": np.random.uniform(2, 35, num_companies).round(2),
        "return_on_capital_employed_pct": np.random.uniform(5, 40, num_companies).round(2),
        "net_profit_margin_pct": np.random.uniform(3, 25, num_companies).round(2),
        "debt_to_equity": np.random.uniform(0.0, 2.5, num_companies).round(2),
        "free_cash_flow_cr": np.random.uniform(-500, 10000, num_companies).round(2),
        "revenue_cagr_5yr": np.random.uniform(-5, 25, num_companies).round(2),
        "pat_cagr_5yr": np.random.uniform(-10, 30, num_companies).round(2),
        "eps_cagr_5yr": np.random.uniform(-10, 30, num_companies).round(2),
        "pe_ratio": np.random.uniform(8, 80, num_companies).round(2),
        "pb_ratio": np.random.uniform(1, 15, num_companies).round(2),
        "dividend_yield_pct": np.random.uniform(0, 5, num_companies).round(2),
        "dividend_payout_ratio_pct": np.random.uniform(0, 90, num_companies).round(2),
        "interest_coverage": np.random.uniform(1, 50, num_companies).round(2),
        "asset_turnover": np.random.uniform(0.3, 3.0, num_companies).round(2),
        "year": year
    }
    df = pd.DataFrame(data)
    
    peer_groups_df = pd.DataFrame({
        "company_id": company_ids,
        "peer_group_name": sectors
    })
    
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect("data/n100_platform.db")
    df.to_sql("financial_ratios", conn, if_exists="replace", index=False)
    peer_groups_df.to_sql("peer_groups", conn, if_exists="replace", index=False)
    conn.close()
    
    return df, peer_groups_df

def main():
    print("--- Running N100 Financial Intelligence Platform (Sprint 3) ---")
    
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect("data/n100_platform.db")
    try:
        df = pd.read_sql_query("SELECT * FROM financial_ratios WHERE year = 2024", conn)
        if df.empty:
            df, _ = generate_synthetic_universe()
    except Exception:
        df, _ = generate_synthetic_universe()
    finally:
        conn.close()
        
    if "broad_sector" not in df.columns:
        df["broad_sector"] = "IT Services"

    config = load_screener_config()
    preset_results = {}
    for preset_name, rules in config["presets"].items():
        preset_df = run_screener_preset(df, rules)
        preset_results[preset_name] = preset_df
        print(f"✓ Preset [{preset_name}]: {len(preset_df)} companies passed")
        
    export_screener_excel(preset_results)
    compute_peer_percentiles()
    generate_radar_charts(df)
    export_peer_comparison_excel()
    
    print("--- Pipeline Execution Complete! Deliverables updated in output/ and reports/ ---")

if __name__ == "__main__":
    main()
