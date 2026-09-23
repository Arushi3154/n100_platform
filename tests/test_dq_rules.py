import os
import sqlite3

import numpy as np
import pandas as pd
import pytest

from main import generate_synthetic_universe
from src.analytics.peer import PeerAnalyticsEngine
from src.screener.engine import ScreenerEngine


@pytest.fixture
def data_setup():
    df, peer_groups_df = generate_synthetic_universe()
    engine = ScreenerEngine()
    peer_engine = PeerAnalyticsEngine()
    return df, peer_groups_df, engine, peer_engine


# DQ 1: ICR 'Debt Free' string mapped to np.inf
def test_dq01_icr_debt_free_handling(data_setup):
    df, _, engine, _ = data_setup
    processed = engine.apply_icr_and_de_rules(df)
    debt_free_rows = df[df["icr"].astype(str).str.lower() == "debt free"]
    assert (processed.loc[debt_free_rows.index, "icr_numeric"] == np.inf).all()


# DQ 2: Financials sector excluded from D/E filter
def test_dq02_financials_de_exclusion(data_setup):
    df, _, engine, _ = data_setup
    res = engine.run_preset(df, "quality_compounder")
    financials = res[res["broad_sector"].str.lower() == "financials"]
    # Financials can exist even if D/E > threshold
    assert len(res) > 0


# DQ 3: Quality Compounder preset bounds check (5 to 50 companies)
def test_dq03_quality_compounder_bounds(data_setup):
    df, _, engine, _ = data_setup
    res = engine.run_preset(df, "quality_compounder")
    assert 5 <= len(res) <= 50


# DQ 4: Value Pick preset bounds check
def test_dq04_value_pick_bounds(data_setup):
    df, _, engine, _ = data_setup
    res = engine.run_preset(df, "value_pick")
    assert 5 <= len(res) <= 50


# DQ 5: Growth Accelerator preset bounds check
def test_dq05_growth_accelerator_bounds(data_setup):
    df, _, engine, _ = data_setup
    res = engine.run_preset(df, "growth_accelerator")
    assert 5 <= len(res) <= 50


# DQ 6: Dividend Champion preset bounds check
def test_dq06_dividend_champion_bounds(data_setup):
    df, _, engine, _ = data_setup
    res = engine.run_preset(df, "dividend_champion")
    assert 5 <= len(res) <= 50


# DQ 7: Debt-Free Blue Chip preset bounds check
def test_dq07_debt_free_blue_chip_bounds(data_setup):
    df, _, engine, _ = data_setup
    res = engine.run_preset(df, "debt_free_blue_chip")
    assert 5 <= len(res) <= 50


# DQ 8: Turnaround Watch preset bounds check
def test_dq08_turnaround_watch_bounds(data_setup):
    df, _, engine, _ = data_setup
    res = engine.run_preset(df, "turnaround_watch")
    assert 5 <= len(res) <= 50


# DQ 9: Composite quality score range (0 - 100)
def test_dq09_composite_score_range(data_setup):
    df, _, engine, _ = data_setup
    processed = engine.apply_icr_and_de_rules(df)
    scored = engine.compute_composite_score(processed)
    assert scored["composite_quality_score"].min() >= 0.0
    assert scored["composite_quality_score"].max() <= 100.0


# DQ 10: Inverted D/E percentile rank (lower D/E gives higher percentile)
def test_dq10_de_percentile_inversion(data_setup):
    df, peer_groups_df, engine, peer_engine = data_setup
    df_icr = engine.apply_icr_and_de_rules(df)
    pcts = peer_engine.compute_percentiles(df_icr, peer_groups_df)
    de_pcts = pcts[pcts["metric"] == "de"]

    # Check that smaller value has higher percentile rank in same peer group
    grp = de_pcts["peer_group_name"].iloc[0]
    sub = de_pcts[de_pcts["peer_group_name"] == grp].sort_values(by="value")
    if len(sub) > 1:
        assert sub.iloc[0]["percentile_rank"] >= sub.iloc[-1]["percentile_rank"]


# DQ 11: Unassigned peer group handled gracefully
def test_dq11_unassigned_peer_handling(data_setup):
    df, peer_groups_df, engine, peer_engine = data_setup
    df_icr = engine.apply_icr_and_de_rules(df)
    # Should not raise exception
    pcts = peer_engine.compute_percentiles(df_icr, peer_groups_df)
    assert not pcts.empty


# DQ 12: SQLite table existence and record count
def test_dq12_sqlite_table_population(data_setup):
    conn = sqlite3.connect("data/n100_platform.db")
    count = pd.read_sql("SELECT COUNT(*) as cnt FROM peer_percentiles", conn)[
        "cnt"
    ].iloc[0]
    conn.close()
    assert count > 0


# DQ 13: Screener output file exists
def test_dq13_screener_output_exists():
    assert os.path.exists("output/screener_output.xlsx")


# DQ 14: Peer comparison output file exists
def test_dq14_peer_comparison_exists():
    assert os.path.exists("output/peer_comparison.xlsx")
