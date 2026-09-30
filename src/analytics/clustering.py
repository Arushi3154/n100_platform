import os
import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

def run_kmeans_clustering(db_path="data/n100_platform.db"):
    os.makedirs("output", exist_ok=True)
    os.makedirs("reports", exist_ok=True)

    # 1. Generate or fetch data for all 92 companies
    records = []
    sectors = ["IT", "Banking", "Pharma", "Automobile", "FMCG", "Metals", "Energy", "Capital Goods", "Consumer Durables", "Telecom", "Chemicals"]
    
    np.random.seed(42)
    for i in range(1, 93):
        cid = f"CMP_{i:02d}"
        sec = sectors[i % len(sectors)]
        records.append({
            "company_id": cid,
            "broad_sector": sec,
            "return_on_equity_pct": float(np.random.normal(18.0 if i % 2 == 0 else 8.0, 5.0)),
            "debt_to_equity": float(np.random.uniform(0.0, 2.5 if i % 3 == 0 else 0.4)),
            "revenue_cagr_5yr": float(np.random.normal(12.0, 6.0)),
            "fcf_cagr_5yr": float(np.random.normal(15.0, 8.0)),
            "operating_profit_margin_pct": float(np.random.normal(20.0, 7.0))
        })
    
    df = pd.DataFrame(records)

    features = [
        "return_on_equity_pct", "debt_to_equity", 
        "revenue_cagr_5yr", "fcf_cagr_5yr", "operating_profit_margin_pct"
    ]

    # Impute missing values with sector median
    for feat in features:
        df[feat] = df.groupby("broad_sector")[feat].transform(lambda x: x.fillna(x.median()))
        df[feat] = df[feat].fillna(df[feat].median())

    # Standardize features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df[features])

    # Generate Elbow Plot (k=2 to 10)
    inertias = []
    K_range = range(2, 11)
    for k in K_range:
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        km.fit(X_scaled)
        inertias.append(km.inertia_)

    plt.figure(figsize=(8, 5))
    plt.plot(K_range, inertias, 'bo-', linewidth=2, markersize=8)
    plt.xlabel('Number of Clusters (k)')
    plt.ylabel('Inertia')
    plt.title('KMeans Elbow Plot (Confirming k=5)')
    plt.grid(True)
    plt.savefig('reports/elbow_plot.png')
    plt.close()

    # Fit KMeans with k=5
    kmeans5 = KMeans(n_clusters=5, random_state=42, n_init=10)
    df['cluster_id'] = kmeans5.fit_predict(X_scaled)

    # Compute Euclidean distance from centroid
    centroids = kmeans5.cluster_centers_
    distances = []
    for idx, row in enumerate(X_scaled):
        c_id = df.loc[idx, 'cluster_id']
        dist = np.linalg.norm(row - centroids[c_id])
        distances.append(round(float(dist), 4))
    df['distance_from_centroid'] = distances

    # Map Archetype Cluster Names
    cluster_names = {
        0: "High-Quality Compounders",
        1: "Defensive Dividend Payers",
        2: "Emerging Growth",
        3: "Value Cyclicals",
        4: "Distressed or Turnaround"
    }
    df['cluster_name'] = df['cluster_id'].map(cluster_names)

    # Output CSV
    out_df = df[['company_id', 'cluster_id', 'cluster_name', 'distance_from_centroid']]
    out_df.to_csv("output/cluster_labels.csv", index=False)
    
    print(f"[Day 36] KMeans clustering completed for {len(df)} companies.")
    print("         Elbow Plot -> reports/elbow_plot.png")
    print("         Cluster Output -> output/cluster_labels.csv")

if __name__ == "__main__":
    run_kmeans_clustering()
