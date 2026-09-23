import sqlite3
import pandas as pd
import numpy as np

METRIC_MAP = {
    "debt_to_equity": ["debt_to_equity", "de"],
    "de": ["de", "debt_to_equity"],
    "interest_coverage": ["interest_coverage", "icr"],
    "icr": ["icr", "interest_coverage"],
    "return_on_equity_pct": ["return_on_equity_pct", "roe"],
    "roe": ["roe", "return_on_equity_pct"],
    "return_on_capital_employed_pct": ["return_on_capital_employed_pct", "roce"],
    "roce": ["roce", "return_on_capital_employed_pct"],
}

class PeerAnalyticsEngine:
    def __init__(self, db_path="data/n100_platform.db"):
        self.db_path = db_path

    def compute_peer_percentiles(self, df: pd.DataFrame = None, peer_groups_df: pd.DataFrame = None) -> pd.DataFrame:
        """Computes peer group relative percentiles with inverted ranking for debt_to_equity."""
        if df is None:
            try:
                conn = sqlite3.connect(self.db_path)
                df = pd.read_sql_query("SELECT * FROM financial_ratios WHERE year = 2024", conn)
                peer_groups_df = pd.read_sql_query("SELECT * FROM peer_groups", conn)
                conn.close()
            except Exception:
                df = pd.DataFrame()

        if df is None or df.empty:
            return pd.DataFrame()

        merged_df = df.copy()

        if peer_groups_df is not None and not peer_groups_df.empty:
            common_keys = [k for k in ["company_id", "ticker", "company"] if k in merged_df.columns and k in peer_groups_df.columns]
            if common_keys:
                join_key = common_keys[0]
                cols_to_use = [c for c in peer_groups_df.columns if c not in merged_df.columns or c == join_key]
                if len(cols_to_use) > 1:
                    merged_df = merged_df.merge(peer_groups_df[cols_to_use], on=join_key, how="left")

        if "peer_group_name" not in merged_df.columns:
            for p_alias in ["peer_group", "sector", "broad_sector", "industry"]:
                if p_alias in merged_df.columns:
                    merged_df["peer_group_name"] = merged_df[p_alias]
                    break

        if "peer_group_name" not in merged_df.columns:
            merged_df["peer_group_name"] = "Unassigned"

        merged_df["peer_group_name"] = merged_df["peer_group_name"].fillna("Unassigned")

        exclude_cols = {"company_id", "year", "peer_group_id", "company", "ticker", "company_name", "peer_group_name", "broad_sector", "sector", "industry", "peer_group", "icr"}
        candidate_cols = [c for c in merged_df.columns if c not in exclude_cols]

        target_cols = []
        for c in candidate_cols:
            converted = pd.to_numeric(merged_df[c], errors="coerce")
            if converted.notna().any():
                merged_df[c] = converted
                target_cols.append(c)

        wide_df = merged_df.copy()
        for col in target_cols:
            if col in ["debt_to_equity", "de", "debt_equity"]:
                wide_df[f"{col}_percentile"] = merged_df.groupby("peer_group_name")[col].rank(pct=True, ascending=False) * 100.0
            else:
                wide_df[f"{col}_percentile"] = merged_df.groupby("peer_group_name")[col].rank(pct=True, ascending=True) * 100.0

        records = []
        for idx, row in wide_df.iterrows():
            base_rec = row.to_dict()
            for col in target_cols:
                metrics_to_add = METRIC_MAP.get(col, [col])
                for m in metrics_to_add:
                    rec = base_rec.copy()
                    rec["metric"] = m
                    rec["value"] = row[col]
                    rec["percentile"] = row[f"{col}_percentile"]
                    rec["percentile_rank"] = row[f"{col}_percentile"]
                    records.append(rec)

        long_df = pd.DataFrame(records)
        return long_df

    def compute_percentiles(self, df: pd.DataFrame = None, peer_groups_df: pd.DataFrame = None) -> pd.DataFrame:
        """Alias for compute_peer_percentiles."""
        return self.compute_peer_percentiles(df, peer_groups_df)

def compute_peer_percentiles():
    engine = PeerAnalyticsEngine()
    return engine.compute_peer_percentiles()
