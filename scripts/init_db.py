import sqlite3
import pandas as pd
import numpy as np

DB_PATH = "data/n100_platform.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Drop existing tables to refresh schema
    tables = ["companies", "financial_ratios", "profit_loss", "balance_sheet", "cash_flow", "valuation"]
    for table in tables:
        cursor.execute(f"DROP TABLE IF EXISTS {table}")

    # 1. Create Companies Table
    cursor.execute("""
    CREATE TABLE companies (
        company_id TEXT PRIMARY KEY,
        company_name TEXT,
        ticker TEXT,
        broad_sector TEXT,
        sector TEXT,
        about TEXT,
        capital_allocation_pattern TEXT
    )
    """)

    # 2. Create Profit & Loss Table
    cursor.execute("""
    CREATE TABLE profit_loss (
        company_id TEXT,
        ticker TEXT,
        year INTEGER,
        sales_cr REAL,
        operating_profit_cr REAL,
        net_profit_cr REAL,
        PRIMARY KEY (company_id, year)
    )
    """)

    # 3. Create Balance Sheet Table
    cursor.execute("""
    CREATE TABLE balance_sheet (
        company_id TEXT,
        ticker TEXT,
        year INTEGER,
        equity_capital_cr REAL,
        reserves_cr REAL,
        borrowings_cr REAL,
        total_assets_cr REAL,
        PRIMARY KEY (company_id, year)
    )
    """)

    # 4. Create Cash Flow Table
    cursor.execute("""
    CREATE TABLE cash_flow (
        company_id TEXT,
        ticker TEXT,
        year INTEGER,
        operating_cf_cr REAL,
        investing_cf_cr REAL,
        financing_cf_cr REAL,
        PRIMARY KEY (company_id, year)
    )
    """)

    # 5. Create Financial Ratios Table
    cursor.execute("""
    CREATE TABLE financial_ratios (
        company_id TEXT,
        ticker TEXT,
        year INTEGER,
        return_on_equity_pct REAL,
        return_on_capital_employed_pct REAL,
        net_profit_margin_pct REAL,
        debt_to_equity REAL,
        pe_ratio REAL,
        pb_ratio REAL,
        ev_ebitda REAL,
        revenue_cagr_5yr REAL,
        free_cash_flow_cr REAL,
        market_cap_cr REAL,
        composite_quality_score REAL,
        PRIMARY KEY (company_id, year)
    )
    """)

    # Seed Sample Nifty 100 Companies
    sample_companies = [
        ("RELIANCE", "Reliance Industries Ltd.", "RELIANCE", "Energy", "Oil & Gas", "India's largest private sector corporation.", "Growth Reinvestment"),
        ("TCS", "Tata Consultancy Services Ltd.", "TCS", "Technology", "IT Services", "Global leader in IT services and consulting.", "Dividend & Buyback"),
        ("INFY", "Infosys Ltd.", "INFY", "Technology", "IT Services", "Next-generation digital services and consulting.", "Dividend & Buyback"),
        ("HDFCBANK", "HDFC Bank Ltd.", "HDFCBANK", "Financial Services", "Private Sector Bank", "Leading private sector bank in India.", "High Capital Retention"),
        ("ITC", "ITC Ltd.", "ITC", "Consumer Goods", "FMCG", "Diversified conglomerate in FMCG, Hotels, and Agri.", "High Dividend Yield"),
        ("LT", "Larsen & Toubro Ltd.", "LT", "Industrials", "Construction & Engineering", "Infrastructure and engineering multinational.", "Capital Intensive Growth"),
        ("BHARTIARTL", "Bharti Airtel Ltd.", "BHARTIARTL", "Telecommunications", "Telecom Services", "Leading global telecommunications company.", "Deleveraging & Network Expansion"),
        ("TATAMOTORS", "Tata Motors Ltd.", "TATAMOTORS", "Automobile", "Auto OEM", "Global automotive manufacturer.", "Deleveraging & R&D")
    ]

    cursor.executemany("""
    INSERT INTO companies VALUES (?, ?, ?, ?, ?, ?, ?)
    """, sample_companies)

    # Seed 10 Years of Historical Data (2015-2024)
    years = list(range(2015, 2025))
    
    pl_rows, bs_rows, cf_rows, ratio_rows = [], [], [], []

    for comp in sample_companies:
        cid, name, ticker, broad_sec, sec, _, _ = comp
        base_rev = np.random.uniform(20000, 150000)
        
        for y in years:
            growth = np.random.uniform(0.05, 0.18)
            sales = base_rev * ((1 + growth) ** (y - 2015))
            op_profit = sales * np.random.uniform(0.15, 0.28)
            net_profit = sales * np.random.uniform(0.08, 0.18)

            pl_rows.append((cid, ticker, y, round(sales, 2), round(op_profit, 2), round(net_profit, 2)))
            bs_rows.append((cid, ticker, y, 1000.0, round(net_profit * 4, 2), round(sales * 0.2, 2), round(sales * 1.5, 2)))
            cf_rows.append((cid, ticker, y, round(net_profit * 1.1, 2), round(-net_profit * 0.5, 2), round(-net_profit * 0.4, 2)))

            roe = np.random.uniform(12.0, 32.0)
            roce = roe * np.random.uniform(0.9, 1.2)
            npm = (net_profit / sales) * 100.0
            de = np.random.uniform(0.0, 0.8) if broad_sec != "Financial Services" else np.random.uniform(3.0, 6.0)
            pe = np.random.uniform(15.0, 55.0)
            pb = np.random.uniform(2.0, 12.0)
            ev_ebitda = pe * 0.75
            cagr = np.random.uniform(8.0, 20.0)
            fcf = round(net_profit * 0.6, 2)
            mcap = round(net_profit * pe, 2)
            score = round(roe * 0.4 + (100 - pe) * 0.2 + (1 / (de + 0.1)) * 10, 1)

            ratio_rows.append((cid, ticker, y, round(roe, 2), round(roce, 2), round(npm, 2), round(de, 2), round(pe, 2), round(pb, 2), round(ev_ebitda, 2), round(cagr, 2), fcf, mcap, score))

    cursor.executemany("INSERT INTO profit_loss VALUES (?, ?, ?, ?, ?, ?)", pl_rows)
    cursor.executemany("INSERT INTO balance_sheet VALUES (?, ?, ?, ?, ?, ?, ?)", bs_rows)
    cursor.executemany("INSERT INTO cash_flow VALUES (?, ?, ?, ?, ?, ?)", cf_rows)
    cursor.executemany("INSERT INTO financial_ratios VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", ratio_rows)

    conn.commit()
    conn.close()
    print(" Database `data/n100_platform.db` successfully populated with all required tables!")

if __name__ == "__main__":
    init_db()
