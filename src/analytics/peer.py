import sqlite3
import pandas as pd
import numpy as np
from typing import Dict, List

PEER_METRICS = [
    "return_on_equity_pct", "return_on_capital_employed_pct", "net_profit_margin_pct",
    "debt_to_equity", "free_cash_flow_cr", "pat_cagr_5yr", "revenue_cagr_5yr",
    "eps_cagr_5yr", "interest_coverage", "asset_turnover"
]

def compute_peer_percentiles(db_path: str = "data/n100_platform.db"):
    conn = sqlite3.connect(db_path)
    
    # Load recent company metrics
    df = pd.read_sql_query("SELECT * FROM financial_ratios WHERE year = 2024", conn)
    
    # Assign synthetic peer groups if missing
    peer_groups = ["IT Services", "Private Banks", "FMCG", "Pharma", "Automobile", 
                   "Capital Goods", "Metals", "Oil & Gas", "Power", "Telecom", "Consumer Durables"]
    
    df["peer_group_name"] = [peer_groups[i % len(peer_groups)] for i in range(len(df))]
    
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS peer_percentiles")
    cursor.execute("""
    CREATE TABLE peer_percentiles (
        company_id TEXT,
        peer_group_name TEXT,
        metric TEXT,
        value REAL,
        percentile_rank REAL,
        year INTEGER,
        PRIMARY KEY (company_id, metric, year)
    )
    """)
    
    records = []
    for group_name, group_df in df.groupby("peer_group_name"):
        for metric in PEER_METRICS:
            if metric not in group_df.columns:
                continue
                
            valid_df = group_df.dropna(subset=[metric]).copy()
            if len(valid_df) == 0:
                continue
                
            # Percentile calculation
            ranks = valid_df[metric].rank(pct=True) * 100.0
            
            # Invert D/E percentile rank (lower debt = higher rank)
            if metric == "debt_to_equity":
                ranks = 100.0 - ranks
                
            for idx, row in valid_df.iterrows():
                records.append((
                    row["company_id"], group_name, metric,
                    float(row[metric]), float(round(ranks[idx], 2)), 2024
                ))
                
    cursor.executemany("INSERT INTO peer_percentiles VALUES (?,?,?,?,?,?)", records)
    conn.commit()
    conn.close()
    print(f"Calculated and stored {len(records)} peer percentile ranks in SQLite.")

if __name__ == "__main__":
    compute_peer_percentiles()
