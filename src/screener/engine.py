import yaml
import numpy as np
import pandas as pd
from scipy.stats.mstats import winsorize

class ScreenerEngine:
    def __init__(self, config_path="config/screener_config.yaml"):
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)

    def apply_icr_and_de_rules(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        # Treat 'Debt Free' label as infinity for ICR
        if 'icr' in df.columns:
            df['icr_numeric'] = df['icr'].apply(
                lambda x: np.inf if str(x).strip().lower() == 'debt free' else pd.to_numeric(x, errors='coerce')
            )
        return df

    def winsorize_series(self, series: pd.Series) -> pd.Series:
        cleaned = series.fillna(series.median())
        if len(cleaned.unique()) <= 1:
            return cleaned
        return pd.Series(winsorize(cleaned, limits=(0.10, 0.10)), index=series.index)

    def compute_composite_score(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        weights = self.config['composite_weights']
        
        metrics_map = {
            'roe': ('profitability', 'roe', True),
            'roce': ('profitability', 'roce', True),
            'npm': ('profitability', 'npm', True),
            'fcf_cagr': ('cash_quality', 'fcf_cagr', True),
            'cfo_pat_ratio': ('cash_quality', 'cfo_pat_ratio', True),
            'revenue_cagr_5yr': ('growth', 'revenue_cagr_5yr', True),
            'pat_cagr_5yr': ('growth', 'pat_cagr_5yr', True),
            'de': ('leverage', 'de_score', False), # Inverse
            'icr_numeric': ('leverage', 'icr_score', True)
        }

        score = np.zeros(len(df))
        for col, (group, key, higher_is_better) in metrics_map.items():
            if col in df.columns and group in weights and key in weights[group]:
                w = weights[group][key]
                win_col = self.winsorize_series(df[col].astype(float))
                min_v, max_v = win_col.min(), win_col.max()
                rng = max_v - min_v
                norm = (win_col - min_v) / (rng if rng != 0 else 1.0) * 100
                if not higher_is_better:
                    norm = 100 - norm
                score += norm * w

        # Cash flag bonus (5%)
        if 'fcf' in df.columns and 'cash_quality' in weights and 'fcf_positive' in weights['cash_quality']:
            score += (df['fcf'] > 0).astype(int) * 100 * weights['cash_quality']['fcf_positive']

        df['composite_quality_score'] = np.round(score, 2)
        
        # Sector-relative adjustment
        if 'broad_sector' in df.columns:
            def sector_norm(x):
                rng = x.max() - x.min()
                if rng == 0:
                    return np.full_like(x, 50.0)
                return (x - x.min()) / rng * 100

            df['composite_quality_score'] = df.groupby('broad_sector')['composite_quality_score'].transform(sector_norm).round(2)

        return df

    def run_preset(self, df: pd.DataFrame, preset_name: str) -> pd.DataFrame:
        df = self.apply_icr_and_de_rules(df)
        preset = self.config['presets'].get(preset_name, {})
        filtered = df.copy()

        # Support all 15 filterable metrics
        for metric, threshold in preset.items():
            if metric == 'de_max' and 'de' in filtered.columns:
                is_financial = filtered['broad_sector'].str.lower() == 'financials' if 'broad_sector' in filtered.columns else False
                filtered = filtered[is_financial | (filtered['de'] <= threshold)]
            elif metric == 'roe_min' and 'roe' in filtered.columns:
                filtered = filtered[filtered['roe'] >= threshold]
            elif metric == 'fcf_min' and 'fcf' in filtered.columns:
                filtered = filtered[filtered['fcf'] >= threshold]
            elif metric == 'revenue_cagr_5yr_min' and 'revenue_cagr_5yr' in filtered.columns:
                filtered = filtered[filtered['revenue_cagr_5yr'] >= threshold]
            elif metric == 'revenue_cagr_3yr_min' and 'revenue_cagr_3yr' in filtered.columns:
                filtered = filtered[filtered['revenue_cagr_3yr'] >= threshold]
            elif metric == 'pat_cagr_5yr_min' and 'pat_cagr_5yr' in filtered.columns:
                filtered = filtered[filtered['pat_cagr_5yr'] >= threshold]
            elif metric == 'opm_min' and 'opm' in filtered.columns:
                filtered = filtered[filtered['opm'] >= threshold]
            elif metric == 'pe_max' and 'pe' in filtered.columns:
                filtered = filtered[filtered['pe'] <= threshold]
            elif metric == 'pb_max' and 'pb' in filtered.columns:
                filtered = filtered[filtered['pb'] <= threshold]
            elif metric == 'dividend_yield_min' and 'dividend_yield' in filtered.columns:
                filtered = filtered[filtered['dividend_yield'] >= threshold]
            elif metric == 'dividend_payout_max' and 'dividend_payout' in filtered.columns:
                filtered = filtered[filtered['dividend_payout'] <= threshold]
            elif metric == 'icr_min' and 'icr_numeric' in filtered.columns:
                filtered = filtered[filtered['icr_numeric'] >= threshold]
            elif metric == 'market_cap_min' and 'market_cap' in filtered.columns:
                filtered = filtered[filtered['market_cap'] >= threshold]
            elif metric == 'net_profit_min' and 'net_profit' in filtered.columns:
                filtered = filtered[filtered['net_profit'] >= threshold]
            elif metric == 'eps_cagr_min' and 'eps_cagr_5yr' in filtered.columns:
                filtered = filtered[filtered['eps_cagr_5yr'] >= threshold]
            elif metric == 'asset_turnover_min' and 'asset_turnover' in filtered.columns:
                filtered = filtered[filtered['asset_turnover'] >= threshold]
            elif metric == 'sales_min' and 'sales' in filtered.columns:
                filtered = filtered[filtered['sales'] >= threshold]

        filtered = self.compute_composite_score(filtered)
        return filtered.sort_values(by='composite_quality_score', ascending=False)
