import streamlit as st
import plotly.express as px
from src.dashboard.utils.db import get_companies, get_ratios

st.title("Market Overview & Macro KPIs")

year = st.sidebar.selectbox("Select Financial Year", options=[2024, 2023, 2022, 2021, 2020, 2019], index=0)

ratios = get_ratios(year=year)
companies = get_companies()
df = ratios.merge(companies, on="company_id", how="left")

if df.empty:
    st.warning("No data found for selected year.")
else:
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    avg_roe = df["return_on_equity_pct"].mean() if "return_on_equity_pct" in df else 0
    med_pe = df["pe_ratio"].median() if "pe_ratio" in df else 0
    med_de = df["debt_to_equity"].median() if "debt_to_equity" in df else 0
    tot_comp = len(df)
    med_cagr = df["revenue_cagr_5yr"].median() if "revenue_cagr_5yr" in df else 0
    debt_free = len(df[df["debt_to_equity"] <= 0.1]) if "debt_to_equity" in df else 0

    col1.metric("Average ROE", f"{avg_roe:.1f}%")
    col2.metric("Median P/E", f"{med_pe:.1f}x")
    col3.metric("Median D/E", f"{med_de:.2f}")
    col4.metric("Total Companies", f"{tot_comp}")
    col5.metric("Median Rev CAGR 5Y", f"{med_cagr:.1f}%")
    col6.metric("Debt-Free Count", f"{debt_free}")

    st.markdown("---")
    c1, c2 = st.columns([1, 1])

    with c1:
        st.subheader("Sector Composition")
        sector_counts = df["broad_sector"].value_counts().reset_index()
        sector_counts.columns = ["Sector", "Companies"]
        fig_donut = px.pie(
            sector_counts, values="Companies", names="Sector", hole=0.4,
            title="Company Distribution Across 11 Broad Sectors"
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    with c2:
        st.subheader("Top 5 Companies by Quality Score")
        if "composite_quality_score" in df.columns:
            top5 = df.sort_values(by="composite_quality_score", ascending=False).head(5)
            cols = [c for c in ["company_name", "broad_sector", "composite_quality_score", "return_on_equity_pct", "pe_ratio"] if c in top5.columns]
            st.dataframe(top5[cols].reset_index(drop=True), use_container_width=True)
        else:
            st.info("Quality score data pending pipeline compute.")
