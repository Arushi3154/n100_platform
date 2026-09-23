import sqlite3
import pandas as pd
import numpy as np
import logging
from src.analytics.ratios import compute_profitability_ratios, compute_leverage_efficiency_ratios
from src.analytics.cagr import compute_cagr
from src.analytics.cashflow_kpis import (
    compute_free_cash_flow, compute_cfo_quality_score,
    compute_capex_intensity, compute_fcf_conversion, classify_capital_allocation
)

logging.basicConfig(filename="output/ratio_edge_cases.log", level=logging.INFO, format="%(asctime)s - %(message)s")

def populate_sprint2_data():
    db_path = "data/n100_platform.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS financial_ratios")
    cursor.execute("""
    CREATE TABLE financial_ratios (
        company_id TEXT,
        year INTEGER,
        net_profit_margin_pct REAL,
        operating_profit_margin_pct REAL,
        return_on_equity_pct REAL,
        debt_to_equity REAL,
        interest_coverage REAL,
        asset_turnover REAL,
        free_cash_flow_cr REAL,
        capex_cr REAL,
        earnings_per_share REAL,
        book_value_per_share REAL,
        dividend_payout_ratio_pct REAL,
        total_debt_cr REAL,
        cash_from_operations_cr REAL,
        revenue_cagr_5yr REAL,
        pat_cagr_5yr REAL,
        eps_cagr_5yr REAL,
        composite_quality_score REAL,
        PRIMARY KEY (company_id, year)
    )
    """)

    np.random.seed(42)
    companies = [f"COMP_{i:03d}" for i in range(1, 93)]
    sectors = ["IT", "FINANCIALS", "CONSUMER", "INDUSTRIAL", "HEALTHCARE"]
    years = list(range(2013, 2025))

    ratio_rows = []
    allocation_rows = []

    for comp_idx, comp_id in enumerate(companies):
        sector = sectors[comp_idx % len(sectors)]
        
        for yr_idx, yr in enumerate(years):
            sales = float(np.random.uniform(500, 10000))
            net_profit = float(sales * np.random.uniform(0.05, 0.25))
            op_profit = float(sales * np.random.uniform(0.12, 0.35))
            equity = float(np.random.uniform(200, 3000))
            reserves = float(equity * 0.5)
            borrowings = 0.0 if (sector == "IT" and yr_idx % 2 == 0) else float(np.random.uniform(0, 1500))
            interest = 0.0 if borrowings == 0 else float(borrowings * 0.08)
            assets = float(equity + reserves + borrowings + np.random.uniform(100, 500))
            ebit = float(op_profit * 0.9)
            other_inc = float(np.random.uniform(5, 50))
            investments = float(np.random.uniform(10, 200))
            
            cfo = float(net_profit * np.random.uniform(0.8, 1.3))
            cfi = -float(sales * np.random.uniform(0.03, 0.10))
            cff = -float(cfo + cfi - np.random.uniform(-20, 20))

            prof = compute_profitability_ratios(net_profit, sales, op_profit, op_profit/sales*100, ebit, equity, reserves, borrowings, assets, sector)
            lev = compute_leverage_efficiency_ratios(borrowings, equity, reserves, op_profit, other_inc, interest, investments, sales, assets, sector)
            
            fcf = compute_free_cash_flow(cfo, cfi)
            fcf_conv = compute_fcf_conversion(fcf, op_profit)
            capex_pct, capex_lbl = compute_capex_intensity(cfi, sales)
            cfo_pat_r, cfo_lbl = compute_cfo_quality_score(cfo, net_profit)
            
            rev_cagr, _ = compute_cagr(sales * 0.6, sales, 5)
            pat_cagr, _ = compute_cagr(net_profit * 0.5, net_profit, 5)
            eps = round(net_profit / 10.0, 2)
            eps_cagr, _ = compute_cagr(eps * 0.5, eps, 5)
            bvps = round((equity + reserves) / 10.0, 2)

            pattern_lbl = classify_capital_allocation(cfo, cfi, cff, cfo_pat_r)
            allocation_rows.append({
                "company_id": comp_id, "year": yr,
                "cfo_sign": "+" if cfo > 0 else "-",
                "cfi_sign": "+" if cfi > 0 else "-",
                "cff_sign": "+" if cff > 0 else "-",
                "pattern_label": pattern_lbl
            })

            ratio_rows.append((
                comp_id, yr, prof["net_profit_margin_pct"], prof["operating_profit_margin_pct"],
                prof["return_on_equity_pct"], lev["debt_to_equity"], lev["interest_coverage"],
                lev["asset_turnover"], fcf, abs(cfi), eps, bvps, 30.0, borrowings, cfo,
                rev_cagr, pat_cagr, eps_cagr, 85.5
            ))

    cursor.executemany("""
    INSERT INTO financial_ratios VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, ratio_rows)

    conn.commit()
    conn.close()

    pd.DataFrame(allocation_rows).to_csv("output/capital_allocation.csv", index=False)
    print("Database populated and capital allocation output generated.")

if __name__ == "__main__":
    populate_sprint2_data()
