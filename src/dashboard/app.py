import streamlit as st

st.set_page_config(
    page_title="Nifty 100 Analytics",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Nifty 100 Financial Analytics & Valuation Platform")
st.sidebar.title("Navigation")
st.sidebar.info("Use the multi-page menu above to switch between analysis screens.")

st.markdown("""
### Welcome to the Nifty 100 Analytics Workspace

This dashboard covers 92 non-financial & financial Nifty 100 constituents across 8 functional screens:

1. **01 Home** — Market-wide KPIs, Sector Donut Breakdown, and Quality Rankings
2. **02 Profile** — 10-Year Fundamental Analysis, Financial Statement Trends, and Pros/Cons
3. **03 Screener** — 10-Metric Quantitative Screener with Preset Strategies and CSV Export
4. **04 Peers** — Multi-Metric Peer Radar Chart and Side-by-Side KPI Benchmarking
5. **05 Trends** — Multi-Metric Overlay Line Charts with YoY Growth Calculations
6. **06 Sectors** — Multi-Variable Scatter Bubble Chart (Revenue vs ROE vs Market Cap)
7. **07 Capital** — Treemap Classification across 8 Capital Allocation Strategies
8. **08 Reports** — Annual Report Direct Link Repository with Verification Badges
""")
