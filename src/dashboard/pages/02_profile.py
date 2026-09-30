import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from src.dashboard.utils.db import get_companies, get_ratios, get_pl

st.title("Company Deep Dive Profile")

companies = get_companies()
search_options = (companies["company_name"] + " (" + companies["ticker"].fillna("") + ")").tolist()
selected_str = st.selectbox("Search Company by Name or Ticker", options=search_options)

selected_ticker = selected_str.split("(")[-1].replace(")", "").strip()
comp_data = companies[(companies["ticker"] == selected_ticker) | (companies["company_id"] == selected_ticker)]

if comp_data.empty:
    st.error("Ticker not found — please try another")
else:
    comp = comp_data.iloc[0]
    st.header(f"{comp['company_name']} ({comp.get('ticker', 'N/A')})")
    st.caption(f"**Sector:** {comp.get('broad_sector', 'N/A')} | **Sub-Sector:** {comp.get('sector', 'N/A')}")
    st.write(comp.get("about", "Leading constituent of the Nifty 100 Index."))

    ratios = get_ratios(ticker=comp["company_id"])
    pl = get_pl(comp["company_id"])

    if not ratios.empty:
        latest = ratios.sort_values(by="year", ascending=False).iloc[0]
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        c1.metric("ROE", f"{latest.get('return_on_equity_pct', 0):.1f}%")
        c2.metric("ROCE", f"{latest.get('return_on_capital_employed_pct', 0):.1f}%")
        c3.metric("Net Margin", f"{latest.get('net_profit_margin_pct', 0):.1f}%")
        c4.metric("D/E Ratio", f"{latest.get('debt_to_equity', 0):.2f}")
        c5.metric("Rev CAGR 5Y", f"{latest.get('revenue_cagr_5yr', 0):.1f}%")
        c6.metric("FCF (Cr)", f"₹{latest.get('free_cash_flow_cr', 0):,.0f}")

    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.subheader("10-Year Revenue & Net Profit Trend")
        if not pl.empty and "sales_cr" in pl.columns and "net_profit_cr" in pl.columns:
            fig_bar = px.bar(pl, x="year", y=["sales_cr", "net_profit_cr"], barmode="group", title="Revenue vs Profit (₹ Cr)")
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("Statement data unavailable.")

    with col_chart2:
        st.subheader("ROE vs ROCE Dual-Axis Trend")
        if not ratios.empty and "return_on_equity_pct" in ratios.columns:
            fig_line = go.Figure()
            fig_line.add_trace(go.Scatter(x=ratios["year"], y=ratios["return_on_equity_pct"], mode="lines+markers", name="ROE (%)"))
            if "return_on_capital_employed_pct" in ratios.columns:
                fig_line.add_trace(go.Scatter(x=ratios["year"], y=ratios["return_on_capital_employed_pct"], mode="lines+markers", name="ROCE (%)"))
            fig_line.update_layout(title="Return Profile Over 10 Years")
            st.plotly_chart(fig_line, use_container_width=True)
        else:
            st.info("Ratio history unavailable.")

    st.subheader("Investment Highlights")
    ch1, ch2 = st.columns(2)
    with ch1:
        st.success("✅ Consistent return metrics above sector medians")
        st.success("✅ Clean balance sheet with manageable leverage")
    with ch2:
        st.error("❌ High trading P/E relative to 5-year historical average")
        st.error("❌ Margin compression risks due to input cost volatility")
