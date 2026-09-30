import streamlit as st
import pandas as pd
from src.dashboard.utils.db import get_companies, get_ratios

st.title("Quantitative Equity Screener")

ratios = get_ratios(year=2024)
companies = get_companies()
df = ratios.merge(companies, on="company_id", how="left")

st.sidebar.header("Presets")
col_p1, col_p2 = st.sidebar.columns(2)

if col_p1.button("Quality"):
    st.session_state.update({"roe": 15.0, "de": 0.5, "pe": 40.0})
if col_p2.button("Value"):
    st.session_state.update({"roe": 10.0, "de": 1.0, "pe": 15.0})
if col_p1.button("Growth"):
    st.session_state.update({"roe": 12.0, "cagr": 12.0})
if col_p2.button("Debt-Free"):
    st.session_state.update({"de": 0.1})

st.sidebar.header("Filter Sliders")
roe_min = st.sidebar.slider("Min ROE (%)", 0.0, 50.0, st.session_state.get("roe", 10.0))
de_max = st.sidebar.slider("Max D/E", 0.0, 5.0, st.session_state.get("de", 2.0))
pe_max = st.sidebar.slider("Max P/E", 0.0, 100.0, st.session_state.get("pe", 60.0))
cagr_min = st.sidebar.slider("Min Rev CAGR 5Y (%)", -10.0, 40.0, st.session_state.get("cagr", 0.0))

filtered = df[
    (df.get("return_on_equity_pct", 0) >= roe_min) &
    (df.get("debt_to_equity", 0) <= de_max) &
    (df.get("pe_ratio", 0) <= pe_max) &
    (df.get("revenue_cagr_5yr", 0) >= cagr_min)
]

st.markdown(f"### **{len(filtered)} companies match your filters**")

display_cols = [c for c in ["company_id", "company_name", "broad_sector", "return_on_equity_pct", "debt_to_equity", "pe_ratio", "revenue_cagr_5yr", "free_cash_flow_cr"] if c in filtered.columns]
st.dataframe(filtered[display_cols].reset_index(drop=True), use_container_width=True)

csv_data = filtered[display_cols].to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Export Filtered Results to CSV",
    data=csv_data,
    file_name="nifty100_screener_results.csv",
    mime="text/csv"
)
