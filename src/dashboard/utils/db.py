import sqlite3
import pandas as pd
import streamlit as st

DB_PATH = "data/n100_platform.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

@st.cache_data(ttl=600)
def get_companies():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM companies", conn)
    conn.close()
    return df

@st.cache_data(ttl=600)
def get_ratios(ticker=None, year=None):
    conn = get_connection()
    query = "SELECT * FROM financial_ratios WHERE 1=1"
    params = []
    if ticker:
        query += " AND (ticker = ? OR company_id = ?)"
        params.extend([ticker, ticker])
    if year:
        query += " AND year = ?"
        params.append(year)
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

@st.cache_data(ttl=600)
def get_pl(ticker):
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM profit_loss WHERE ticker = ? OR company_id = ? ORDER BY year ASC", conn, params=[ticker, ticker])
    conn.close()
    return df

@st.cache_data(ttl=600)
def get_bs(ticker):
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM balance_sheet WHERE ticker = ? OR company_id = ? ORDER BY year ASC", conn, params=[ticker, ticker])
    conn.close()
    return df

@st.cache_data(ttl=600)
def get_cf(ticker):
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM cash_flow WHERE ticker = ? OR company_id = ? ORDER BY year ASC", conn, params=[ticker, ticker])
    conn.close()
    return df

@st.cache_data(ttl=600)
def get_sectors():
    conn = get_connection()
    df = pd.read_sql_query("SELECT DISTINCT broad_sector FROM companies WHERE broad_sector IS NOT NULL", conn)
    conn.close()
    return sorted(df["broad_sector"].dropna().tolist())

@st.cache_data(ttl=600)
def get_peers(group_name):
    conn = get_connection()
    query = """
        SELECT c.company_id, c.company_name, c.ticker, c.broad_sector, c.sector, r.* 
        FROM companies c 
        JOIN financial_ratios r ON c.company_id = r.company_id 
        WHERE (c.broad_sector = ? OR c.sector = ?)
        AND r.year = (SELECT MAX(year) FROM financial_ratios)
    """
    df = pd.read_sql_query(query, conn, params=[group_name, group_name])
    conn.close()
    return df

@st.cache_data(ttl=600)
def get_valuation(ticker=None):
    conn = get_connection()
    if ticker:
        df = pd.read_sql_query("SELECT * FROM valuation WHERE ticker = ? OR company_id = ?", conn, params=[ticker, ticker])
    else:
        df = pd.read_sql_query("SELECT * FROM valuation", conn)
    conn.close()
    return df
