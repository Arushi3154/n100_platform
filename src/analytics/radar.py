import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def generate_radar_charts(
    df: pd.DataFrame, peer_groups_df: pd.DataFrame, output_dir="reports/radar_charts"
):
    os.makedirs(output_dir, exist_ok=True)
    merged = df.merge(peer_groups_df, on="company_id", how="left")

    axes_metrics = [
        "roe",
        "roce",
        "npm",
        "de",
        "fcf",
        "pat_cagr_5yr",
        "revenue_cagr_5yr",
        "composite_quality_score",
    ]
    labels = [
        "ROE",
        "ROCE",
        "NPM",
        "D/E (Inv)",
        "FCF",
        "PAT CAGR",
        "Rev CAGR",
        "Composite",
    ]

    num_vars = len(labels)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles += angles[:1]

    for _, row in merged.iterrows():
        fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))

        comp_vals = [row.get(m, 0) for m in axes_metrics]
        comp_vals += comp_vals[:1]

        peer_group = row.get("peer_group_name")
        if pd.notna(peer_group):
            peer_avg = (
                merged[merged["peer_group_name"] == peer_group][axes_metrics]
                .mean()
                .tolist()
            )
            peer_avg += peer_avg[:1]
            ax.plot(
                angles,
                peer_avg,
                color="gray",
                linestyle="--",
                linewidth=1.5,
                label=f"Peer Avg ({peer_group})",
            )
        else:
            nifty_avg = merged[axes_metrics].mean().tolist()
            nifty_avg += nifty_avg[:1]
            ax.plot(
                angles,
                nifty_avg,
                color="orange",
                linestyle="--",
                linewidth=1.5,
                label="Nifty 100 Avg",
            )

        ax.plot(
            angles, comp_vals, color="#1f77b4", linewidth=2, label=row["company_id"]
        )
        ax.fill(angles, comp_vals, color="#1f77b4", alpha=0.25)

        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(labels, fontsize=9)
        ax.set_title(
            f"{row['company_id']} - Peer Comparison",
            y=1.08,
            fontsize=12,
            fontweight="bold",
        )
        ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1), fontsize=8)

        plt.tight_layout()
        plt.savefig(f"{output_dir}/{row['company_id']}_radar.png")
        plt.close()
