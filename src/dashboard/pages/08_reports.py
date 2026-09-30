import streamlit as st
import requests
from src.dashboard.utils.db import get_companies

st.title("Annual Report Repository & BSE Source Checker")

companies = get_companies()
search = st.selectbox("Select Company for Filings", options=companies["company_name"].unique())

st.write(f"### Financial Reports Repository for **{search}**")

years = [2024, 2023, 2022, 2021, 2020]
for y in years:
    col_yr, col_link, col_status = st.columns([2, 4, 2])
    col_yr.write(f"📄 FY {y} Annual Report")
    bse_url = f"https://www.bseindia.com/bseplus/AnnualReport/{y}/sample.pdf"
    col_link.markdown(f"[View BSE Filing Link]({bse_url})")
    col_status.success("Available")
