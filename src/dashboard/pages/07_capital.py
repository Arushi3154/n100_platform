import streamlit as st
import plotly.express as px
from src.dashboard.utils.db import get_companies

st.title("Capital Allocation Map")

companies = get_companies()
if "capital_allocation_pattern" not in companies.columns:
    companies["capital_allocation_pattern"] = "Balanced Allocation"

fig_treemap = px.treemap(
    companies,
    path=["capital_allocation_pattern", "broad_sector", "company_name"],
    title="Nifty 100 Constituents Grouped by Capital Allocation Archetypes"
)
st.plotly_chart(fig_treemap, use_container_width=True)

pattern = st.selectbox("Filter Companies by Strategy Pattern", options=companies["capital_allocation_pattern"].unique())
st.dataframe(companies[companies["capital_allocation_pattern"] == pattern][["company_name", "broad_sector", "ticker"]], use_container_width=True)
