import streamlit as st
import plotly.express as px
from src.dashboard.utils.db import get_companies, get_ratios

st.title("Sector Dynamics & Competitive Positioning")

ratios = get_ratios(year=2024)
companies = get_companies()
df = ratios.merge(companies, on="company_id", how="left")

if not df.empty:
    fig_bubble = px.scatter(
        df,
        x="sales_cr" if "sales_cr" in df else "pe_ratio",
        y="return_on_equity_pct",
        size="market_cap_cr" if "market_cap_cr" in df else None,
        color="broad_sector",
        hover_name="company_name",
        log_x=True,
        title="Sector Bubble Map: Revenue (X) vs ROE (Y) vs Market Cap (Bubble Size)"
    )
    st.plotly_chart(fig_bubble, use_container_width=True)
    
    st.subheader("Sector Median ROE & Valuation Multiples")
    sec_summary = df.groupby("broad_sector")[["return_on_equity_pct", "pe_ratio"]].median().reset_index()
    fig_bar = px.bar(sec_summary, x="broad_sector", y="return_on_equity_pct", title="Median ROE by Broad Sector")
    st.plotly_chart(fig_bar, use_container_width=True)
