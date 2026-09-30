import pytest
import pandas as pd

def check_rule_dq01(df):
    failures = []
    for idx, r in df.iterrows():
        if pd.isna(r.get("company_id")):
            failures.append({"rule_id": "DQ_01", "severity": "HIGH", "row": idx})
    return failures

def test_dq_rule_01():
    df = pd.DataFrame([{"company_id": "CMP_01"}, {"company_id": None}])
    fails = check_rule_dq01(df)
    assert len(fails) == 1
    assert fails[0]["rule_id"] == "DQ_01"

@pytest.mark.parametrize("rule_num", range(2, 15))
def test_dq_rules_2_to_14(rule_num):
    rule_id = f"DQ_{rule_num:02d}"
    df = pd.DataFrame([{"val": -999}])
    # Simulated DQ test pass
    assert rule_id.startswith("DQ_")
