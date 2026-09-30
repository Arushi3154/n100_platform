import streamlit as st
import plotly.graph_objects as go
from src.dashboard.utils.db import get_sectors, get_peers

st.title("Peer Comparison Analysis")

sectors = get_sectors()
selected_sector = st.selectbox("Select Peer Group / Sector", options=sectors)

peers_df = get_peers(selected_sector)

if not peers_df.empty:
    st.write(f"### Peer Group: {selected_sector} ({len(peers_df)} Companies)")
    
    benchmark = st.selectbox("Select Benchmark Company", options=peers_df["company_name"].unique())
    bench_row = peers_df[peers_df["company_name"] == benchmark].iloc[0]
    
    metrics = ["return_on_equity_pct", "return_on_capital_employed_pct", "net_profit_margin_pct", "revenue_cagr_5yr"]
    metrics = [m for m in metrics if m in peers_df.columns]
    
    bench_vals = [bench_row.get(m, 0) or 0 for m in metrics]
    peer_avg_vals = [peers_df[m].mean() or 0 for m in metrics]
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=bench_vals, theta=metrics, fill='toself', name=benchmark))
    fig.add_trace(go.Scatterpolar(r=peer_avg_vals, theta=metrics, fill='toself', name="Peer Average"))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True)), title="Benchmark vs Sector Average Radar")
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("Side-by-Side KPI Matrix")
    show_cols = [c for c in ["company_name", "pe_ratio", "debt_to_equity"] + metrics if c in peers_df.columns]
    st.dataframe(peers_df[show_cols].reset_index(drop=True), use_container_width=True)
else:
    st.info("No peer records available for selected sector.")
