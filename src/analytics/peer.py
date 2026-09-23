import sqlite3
import pandas as pd
import numpy as np
from typing import Dict, List, Optional

PEER_METRICS = [
    "return_on_equity_pct", "return_on_capital_employed_pct", "net_profit_margin_pct",
    "debt_to_equity", "free_cash_flow_cr", "pat_cagr_5yr", "revenue_cagr_5yr",
    "eps_cagr_5yr", "interest_coverage", "asset_turnover"
]

class PeerAnalyticsEngine:
    def __init__(self, db_path: str = "data/n100_platform.db"):
        self.db_path = db_path

    def compute_peer_percentiles(self) -> int:
        conn = sqlite3.connect(self.db_path)
        
        try:
            df = pd.read_sql_query("SELECT * FROM financial_ratios WHERE year = 2024", conn)
        except Exception:
            conn.close()
            return 0
            
        if df.empty:
            conn.close()
            return 0

        peer_groups = ["IT Services", "Financial Services", "FMCG", "Pharma", "Automobile", 
                       "Capital Goods", "Metals", "Oil & Gas", "Power", "Telecom", "Consumer Durables"]
        
        if "peer_group_name" not in df.columns or df["peer_group_name"].isnull().all():
            if "broad_sector" in df.columns and df["broad_sector"].notnull().any():
                df["peer_group_name"] = df["broad_sector"]
            else:
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
                    
                ranks = valid_df[metric].rank(pct=True) * 100.0
                
                if metric == "debt_to_equity":
                    ranks = 100.0 - ranks
                    
                for idx, row in valid_df.iterrows():
                    records.append((
                        str(row["company_id"]), str(group_name), str(metric),
                        float(row[metric]), float(round(ranks[idx], 2)), 2024
                    ))
                    
        cursor.executemany("INSERT INTO peer_percentiles VALUES (?,?,?,?,?,?)", records)
        conn.commit()
        conn.close()
        print(f"Calculated and stored {len(records)} peer percentile ranks in SQLite.")
        return len(records)

def compute_peer_percentiles(db_path: str = "data/n100_platform.db"):
    engine = PeerAnalyticsEngine(db_path=db_path)
    return engine.compute_peer_percentiles()

if __name__ == "__main__":
    compute_peer_percentiles()
