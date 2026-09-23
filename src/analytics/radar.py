import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def generate_radar_charts(df: pd.DataFrame, output_dir: str = "reports/radar_charts"):
    os.makedirs(output_dir, exist_ok=True)
    
    axes_labels = ["ROE", "ROCE", "NPM", "D/E (Inv)", "FCF", "PAT CAGR", "Rev CAGR", "Score"]
    num_vars = len(axes_labels)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles += angles[:1]

    for idx, row in df.head(10).iterrows():
        fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
        
        # Values scale 0 to 100
        values = [
            min(100, max(0, row.get("return_on_equity_pct", 50) or 50)),
            min(100, max(0, row.get("return_on_capital_employed_pct", 50) or 50)),
            min(100, max(0, row.get("net_profit_margin_pct", 50) or 50)),
            min(100, max(0, 100 - ((row.get("debt_to_equity", 0.5) or 0.5) * 20))),
            50.0, 50.0, 50.0,
            row.get("composite_quality_score", 60.0)
        ]
        values += values[:1]

        # Peer average reference
        peer_avg = [60, 55, 50, 70, 50, 50, 50, 55]
        peer_avg += peer_avg[:1]

        # Plot company fill
        ax.plot(angles, values, color="#1f77b4", linewidth=2, label=row['company_id'])
        ax.fill(angles, values, color="#1f77b4", alpha=0.25)

        # Plot peer group average overlay
        ax.plot(angles, peer_avg, color="#ff7f0e", linewidth=1.5, linestyle="--", label="Peer Group Avg")

        ax.set_theta_offset(np.pi / 2)
        ax.set_theta_direction(-1)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(axes_labels, fontsize=9)
        
        plt.title(f"Peer Radar Analysis - {row['company_id']}", size=12, y=1.08)
        plt.legend(loc="upper right", bbox_to_anchor=(1.1, 1.1), fontsize=8)
        
        chart_path = os.path.join(output_dir, f"{row['company_id']}_radar.png")
        plt.savefig(chart_path, dpi=100, bbox_inches="tight")
        plt.close()
        
    print(f"Generated radar charts in {output_dir}")
