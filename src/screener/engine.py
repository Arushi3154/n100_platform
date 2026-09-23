import os
import json
import pandas as pd
import numpy as np

DEFAULT_PRESETS = {
    "quality_compounder": {
        "return_on_equity_pct": (">=", 15.0),
        "return_on_capital_employed_pct": (">=", 15.0),
        "debt_to_equity": ("<=", 0.8),
        "pat_cagr_5yr": (">=", 8.0)
    },
    "value_pick": {
        "pe_ratio": ("<=", 35.0),
        "pb_ratio": ("<=", 4.5),
        "return_on_equity_pct": (">=", 8.0),
        "dividend_yield_pct": (">=", 0.5)
    },
    "growth_accelerator": {
        "revenue_cagr_5yr": (">=", 8.0),
        "pat_cagr_5yr": (">=", 8.0),
        "return_on_capital_employed_pct": (">=", 10.0)
    },
    "dividend_champion": {
        "dividend_yield_pct": (">=", 1.0),
        "dividend_payout_ratio_pct": (">=", 15.0),
        "debt_to_equity": ("<=", 1.5)
    },
    "debt_free_blue_chip": {
        "debt_to_equity": ("<=", 0.2),
        "market_cap_cr": (">=", 10000.0),
        "return_on_equity_pct": (">=", 8.0)
    },
    "turnaround_watch": {
        "revenue_cagr_5yr": (">=", 0.0),
        "pat_cagr_5yr": (">=", 0.0),
        "pe_ratio": ("<=", 50.0)
    }
}

class ScreenerEngine:
    def __init__(self, config=None):
        self.config = config or load_screener_config()

    def apply_icr_and_de_rules(self, df: pd.DataFrame) -> pd.DataFrame:
        """Applies ICR and Debt-to-Equity rules in-place and returns the dataframe."""
        if "interest_coverage" in df.columns:
            ic_series = pd.to_numeric(df["interest_coverage"], errors="coerce")
        elif "icr_numeric" in df.columns:
            ic_series = pd.to_numeric(df["icr_numeric"], errors="coerce")
        else:
            ic_series = pd.Series(np.nan, index=df.index)

        if "debt_to_equity" in df.columns:
            de_series = pd.to_numeric(df["debt_to_equity"], errors="coerce")
        elif "de" in df.columns:
            de_series = pd.to_numeric(df["de"], errors="coerce")
        else:
            de_series = pd.Series(np.nan, index=df.index)

        is_debt_free = (de_series <= 0.05) | ic_series.isna()
        if "icr" in df.columns:
            is_debt_free = is_debt_free | (df["icr"].astype(str).str.lower() == "debt free")

        icr_num = np.where(is_debt_free, np.inf, ic_series.fillna(0.0))
        icr_str = np.where(is_debt_free, "Debt Free", icr_num.astype(str))

        df["icr_numeric"] = icr_num
        df["icr"] = icr_str
        if "interest_coverage" in df.columns:
            df["interest_coverage"] = icr_num

        if "free_cash_flow_cr" in df.columns and "free_cash_flow_cr_score" not in df.columns:
            df["free_cash_flow_cr_score"] = df["free_cash_flow_cr"].rank(pct=True) * 10.0

        return self.compute_composite_score(df)

    def compute_composite_score(self, df: pd.DataFrame) -> pd.DataFrame:
        """Computes composite quality score for screener ranking."""
        roe = df.get("return_on_equity_pct", 0)
        roce = df.get("return_on_capital_employed_pct", 0)
        df["composite_quality_score"] = ((roe + roce) / 2.0).round(2)
        return df

    def run_preset(self, df: pd.DataFrame, preset_name: str) -> pd.DataFrame:
        """Filters dataframe based on configured screener preset rules."""
        df_processed = self.apply_icr_and_de_rules(df)
        
        presets = self.config.get("presets", DEFAULT_PRESETS)
        rules = presets.get(preset_name, DEFAULT_PRESETS.get(preset_name, {}))
        
        filtered_df = df_processed.copy()
        
        if isinstance(rules, dict):
            for col, rule in rules.items():
                if col not in filtered_df.columns:
                    continue
                if isinstance(rule, (list, tuple)) and len(rule) == 2:
                    op, val = rule
                    if op == ">=":
                        filtered_df = filtered_df[filtered_df[col] >= val]
                    elif op == "<=":
                        filtered_df = filtered_df[filtered_df[col] <= val]
                    elif op == ">":
                        filtered_df = filtered_df[filtered_df[col] > val]
                    elif op == "<":
                        filtered_df = filtered_df[filtered_df[col] < val]
                    elif op == "==":
                        filtered_df = filtered_df[filtered_df[col] == val]
        
        return filtered_df

def load_screener_config(config_path: str = "config/screener_config.json") -> dict:
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {"presets": DEFAULT_PRESETS}

def run_screener_preset(df: pd.DataFrame, rules: dict) -> pd.DataFrame:
    engine = ScreenerEngine()
    filtered_df = engine.apply_icr_and_de_rules(df)
    for col, rule in rules.items():
        if col not in filtered_df.columns:
            continue
        if isinstance(rule, (list, tuple)) and len(rule) == 2:
            op, val = rule
            if op == ">=":
                filtered_df = filtered_df[filtered_df[col] >= val]
            elif op == "<=":
                filtered_df = filtered_df[filtered_df[col] <= val]
            elif op == ">":
                filtered_df = filtered_df[filtered_df[col] > val]
            elif op == "<":
                filtered_df = filtered_df[filtered_df[col] < val]
            elif op == "==":
                filtered_df = filtered_df[filtered_df[col] == val]
    return filtered_df

def export_screener_excel(preset_results: dict, output_path: str = "output/screener_results.xlsx"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        for preset_name, res_df in preset_results.items():
            res_df.to_excel(writer, sheet_name=preset_name[:31], index=False)
