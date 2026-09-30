import streamlit as st
import plotly.express as px
from src.dashboard.utils.db import get_companies, get_ratios

st.title("Multi-Metric Historical Trends")

companies = get_companies()
search = st.selectbox("Select Company", options=companies["company_name"].unique())
comp_id = companies[companies["company_name"] == search].iloc[0]["company_id"]

ratios = get_ratios(ticker=comp_id).sort_values(by="year")

available_metrics = [c for c in ["return_on_equity_pct", "return_on_capital_employed_pct", "debt_to_equity", "pe_ratio", "net_profit_margin_pct"] if c in ratios.columns]
selected_metrics = st.multiselect("Select Up to 3 Metrics to Overlay", options=available_metrics, default=available_metrics[:2], max_selections=3)

if not ratios.empty and selected_metrics:
    fig = px.line(ratios, x="year", y=selected_metrics, markers=True, title=f"10-Year Metric Evolution for {search}")
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("Year-over-Year Growth Matrix")
    pct_change = ratios.set_index("year")[selected_metrics].pct_change() * 100
    st.dataframe(pct_change.fillna("N/A"), use_container_width=True)
