import os
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

def generate_profiling_and_stats():
    os.makedirs("output", exist_ok=True)
    os.makedirs("reports", exist_ok=True)

    np.random.seed(42)
    kpis = [
        "roe_pct", "roce_pct", "pe_ratio", "pb_ratio", "debt_to_equity",
        "current_ratio", "operating_margin_pct", "net_margin_pct",
        "revenue_cagr_5yr", "fcf_cagr_5yr"
    ]

    records = []
    sectors = ["IT", "Banking", "Pharma", "Automobile", "FMCG", "Metals", "Energy", "Capital Goods", "Consumer Durables", "Telecom", "Chemicals"]

    for i in range(1, 93):
        cid = f"CMP_{i:02d}"
        sec = sectors[i % len(sectors)]
        row = {
            "company_id": cid,
            "broad_sector": sec,
            "roe_pct": float(np.random.normal(16, 6)),
            "roce_pct": float(np.random.normal(18, 5)),
            "pe_ratio": float(np.random.uniform(10, 50)),
            "pb_ratio": float(np.random.uniform(1.5, 8.0)),
            "debt_to_equity": float(np.random.uniform(0, 2.0)),
            "current_ratio": float(np.random.uniform(0.8, 3.0)),
            "operating_margin_pct": float(np.random.normal(22, 8)),
            "net_margin_pct": float(np.random.normal(14, 5)),
            "revenue_cagr_5yr": float(np.random.normal(12, 6)),
            "fcf_cagr_5yr": float(np.random.normal(15, 8))
        }
        # Inject deliberate outlier
        if i == 42:
            row["debt_to_equity"] = 8.5
        records.append(row)

    df = pd.DataFrame(records)

    # 1. Correlation Matrix Heatmap
    plt.figure(figsize=(10, 8))
    corr = df[kpis].corr()
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", cbar=True)
    plt.title("Pearson Correlation Heatmap of 10 Core KPIs")
    plt.tight_layout()
    plt.savefig("reports/correlation_heatmap.png")
    plt.close()

    # 2. Outlier Detection (Z-score > 3 per broad sector)
    outliers = []
    for sec, group in df.groupby("broad_sector"):
        for kpi in kpis:
            std = group[kpi].std()
            if std > 0:
                z_scores = (group[kpi] - group[kpi].mean()) / std
                outlier_rows = group[np.abs(z_scores) > 3]
                for idx, r in outlier_rows.iterrows():
                    outliers.append({
                        "company_id": r["company_id"],
                        "broad_sector": sec,
                        "metric": kpi,
                        "value": r[kpi],
                        "z_score": round(float(z_scores[idx]), 2)
                    })

    df_outliers = pd.DataFrame(outliers if outliers else [], columns=["company_id", "broad_sector", "metric", "value", "z_score"])
    df_outliers.to_csv("output/outlier_report.csv", index=False)

    # 3. Portfolio Stats (P10, P25, P50, P75, P90, Mean, Std)
    stats_rows = []
    for kpi in kpis:
        s = df[kpi]
        stats_rows.append({
            "kpi": kpi,
            "P10": round(float(s.quantile(0.10)), 2),
            "P25": round(float(s.quantile(0.25)), 2),
            "P50": round(float(s.quantile(0.50)), 2),
            "P75": round(float(s.quantile(0.75)), 2),
            "P90": round(float(s.quantile(0.90)), 2),
            "Mean": round(float(s.mean()), 2),
            "Std": round(float(s.std()), 2)
        })

    df_stats = pd.DataFrame(stats_rows)
    df_stats.to_csv("output/portfolio_stats.csv", index=False)

    print("[Day 37] Profiling, Correlation Heatmap, Outlier Report, & Portfolio Stats complete.")
    print("         Heatmap -> reports/correlation_heatmap.png")
    print("         Outliers -> output/outlier_report.csv")
    print("         Stats -> output/portfolio_stats.csv")

if __name__ == "__main__":
    generate_profiling_and_stats()
