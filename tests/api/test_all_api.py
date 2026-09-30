import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "db_row_counts" in data

def test_companies_endpoint():
    res = client.get("/api/v1/companies")
    assert res.status_code == 200
    assert len(res.json()) == 92

def test_company_by_ticker():
    res = client.get("/api/v1/companies/TCS")
    assert res.status_code == 200
    assert res.json()["ticker"] == "TCS"

def test_company_not_found():
    res = client.get("/api/v1/companies/INVALID_TICKER")
    assert res.status_code == 404

def test_screener_valid():
    res = client.get("/api/v1/screener?min_roe=15")
    assert res.status_code == 200
    for c in res.json():
        assert c["roe_pct"] >= 15

def test_screener_invalid():
    res = client.get("/api/v1/screener?min_roe=-500")
    assert res.status_code == 400

def test_sectors_count():
    res = client.get("/api/v1/sectors")
    assert res.status_code == 200
    assert len(res.json()) == 11

def test_sector_companies():
    res = client.get("/api/v1/sectors/IT/companies")
    assert res.status_code == 200
    assert len(res.json()) > 0

def test_sector_not_found():
    res = client.get("/api/v1/sectors/UNKNOWN_SECTOR/companies")
    assert res.status_code == 404
