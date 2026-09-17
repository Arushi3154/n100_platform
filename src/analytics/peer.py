import sqlite3
import pandas as pd
import numpy as np

class PeerAnalyticsEngine:
    def __init__(self, db_path="data/n100_platform.db"):
        self.db_path = db_path

    def compute_percentiles(self, df: pd.DataFrame, peer_groups_df: pd.DataFrame) -> pd.DataFrame:
        merged = df.merge(peer_groups_df, on="company_id", how="left")
        
        ranking_metrics = [
            'roe', 'roce', 'npm', 'de', 'fcf', 
            'pat_cagr_5yr', 'revenue_cagr_5yr', 'eps_cagr_5yr', 'icr_numeric', 'asset_turnover'
        ]

        results = []
        for idx, row in merged.iterrows():
            peer_group = row.get('peer_group_name')
            if pd.isna(peer_group) or not peer_group:
                # Handle unassigned peer group gracefully
                continue

            group_data = merged[merged['peer_group_name'] == peer_group]

            for metric in ranking_metrics:
                if metric in group_data.columns and not pd.isna(row.get(metric)):
                    val = row[metric]
                    pct = (group_data[metric] < val).mean()
                    
                    # Invert D/E percentile rank (lower leverage = higher percentile)
                    if metric == 'de':
                        pct = 1.0 - (group_data[metric] <= val).mean()

                    results.append({
                        'company_id': row['company_id'],
                        'peer_group_name': peer_group,
                        'metric': metric,
                        'value': val,
                        'percentile_rank': round(pct * 100, 2),
                        'year': row.get('year', 2026)
                    })

        res_df = pd.DataFrame(results)
        self._save_to_sqlite(res_df)
        return res_df

    def _save_to_sqlite(self, df: pd.DataFrame):
        conn = sqlite3.connect(self.db_path)
        df.to_sql("peer_percentiles", conn, if_exists="replace", index=False)
        conn.close()
