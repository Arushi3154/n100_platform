import os
import sqlite3
import pandas as pd
import numpy as np

def run_valuation_pipeline(db_path="data/n100_platform.db", output_dir="output"):
    os.makedirs(output_dir, exist_ok=True)
    conn = sqlite3.connect(db_path)
    
    ratios_df = pd.read_sql_query("SELECT * FROM financial_ratios", conn)
    companies_df = pd.read_sql_query("SELECT * FROM companies", conn)
    conn.close()

    if ratios_df.empty:
        print("financial_ratios table is empty.")
        return None

    latest_year = ratios_df["year"].max()
    df = ratios_df[ratios_df["year"] == latest_year].merge(companies_df, on="company_id", how="left")

    if "broad_sector" not in df.columns:
        df["broad_sector"] = df.get("sector", "General")

    # 1. FCF Yield
    if "free_cash_flow_cr" in df.columns and "market_cap_cr" in df.columns:
        df["FCF_yield_pct"] = (df["free_cash_flow_cr"] / df["market_cap_cr"].replace(0, np.nan)) * 100.0
    else:
        df["FCF_yield_pct"] = np.nan

    # 2. Sector Median PE & Relative PE %
    sector_pe_median = df.groupby("broad_sector")["pe_ratio"].transform("median")
    df["sector_median_PE"] = sector_pe_median
    df["PE_vs_sector_median_pct"] = ((df["pe_ratio"] - sector_pe_median) / sector_pe_median) * 100.0

    # 3. 5yr Median PE Fallback
    if "pe_ratio_5yr_median" in df.columns:
        df["5yr_median_PE"] = df["pe_ratio_5yr_median"]
    else:
        df["5yr_median_PE"] = df["pe_ratio"]

    # 4. Flag Logic
    def assign_flag(row):
        pe = row.get("pe_ratio", np.nan)
        sec_med = row.get("sector_median_PE", np.nan)
        if pd.isna(pe) or pd.isna(sec_med) or sec_med <= 0:
            return "Fair"
        if pe > sec_med * 1.5:
            return "Caution"
        elif pe < sec_med * 0.7:
            return "Discount"
        return "Fair"

    df["flag"] = df.apply(assign_flag, axis=1)

    # 5. Build Deliverable DataFrames
    summary_cols = [
        "company_id", "company_name", "broad_sector", "pe_ratio", "pb_ratio",
        "ev_ebitda", "FCF_yield_pct", "5yr_median_PE", "PE_vs_sector_median_pct", "flag"
    ]
    
    rename_dict = {
        "broad_sector": "sector",
        "pe_ratio": "P/E",
        "pb_ratio": "P/B",
        "ev_ebitda": "EV/EBITDA"
    }

    avail_cols = [c for c in summary_cols if c in df.columns]
    val_summary = df[avail_cols].rename(columns=rename_dict)

    # Export Files
    excel_path = os.path.join(output_dir, "valuation_summary.xlsx")
    val_summary.to_excel(excel_path, index=False)

    flags_csv_path = os.path.join(output_dir, "valuation_flags.csv")
    flags_df = val_summary[val_summary["flag"].isin(["Caution", "Discount"])]
    flags_df.to_csv(flags_csv_path, index=False)

    print(f"✅ Generated: {excel_path} ({len(val_summary)} companies)")
    print(f"✅ Generated: {flags_csv_path} ({len(flags_df)} flagged companies)")
    return val_summary

if __name__ == "__main__":
    run_valuation_pipeline()
