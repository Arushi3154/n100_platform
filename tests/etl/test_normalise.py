import pytest

def normalize_year(val):
    if val is None:
        return None
    s = str(val).strip()
    if len(s) == 4 and s.isdigit():
        return int(s)
    if "FY" in s:
        digits = "".join([c for c in s if c.isdigit()])
        if len(digits) == 2:
            return 2000 + int(digits)
        elif len(digits) == 4:
            return int(digits)
    if "-" in s or "/" in s:
        parts = s.replace("/", "-").split("-")
        if len(parts[0]) == 4 and parts[0].isdigit():
            return int(parts[0])
    return None

def test_normalize_year_variants():
    assert normalize_year("2024") == 2024
    assert normalize_year(2023) == 2023
    assert normalize_year("FY24") == 2024
    assert normalize_year("FY 2022") == 2022
    assert normalize_year("2021-22") == 2021
    assert normalize_year("2020/21") == 2020
    assert normalize_year(None) is None
    assert normalize_year("Invalid") is None

@pytest.mark.parametrize("inp,expected", [
    ("2015", 2015), ("2016", 2016), ("2017", 2017), ("2018", 2018), ("2019", 2019),
    ("2020", 2020), ("2021", 2021), ("2022", 2022), ("2023", 2023), ("2024", 2024),
    ("FY15", 2015), ("FY16", 2016)
])
def test_normalize_year_param(inp, expected):
    assert normalize_year(inp) == expected
