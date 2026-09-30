import os
from fastapi import APIRouter, HTTPException, Query, Response
from fastapi.responses import FileResponse

router = APIRouter()

# Mock dataset for 92 companies
COMPANIES = []
sectors = ["IT", "Banking", "Pharma", "Automobile", "FMCG", "Metals", "Energy", "Capital Goods", "Consumer Durables", "Telecom", "Chemicals"]

for i in range(1, 93):
    cid = f"CMP_{i:02d}"
    ticker = f"TICKER_{i:02d}" if i != 1 else "TCS"
    sec = sectors[i % len(sectors)]
    COMPANIES.append({
        "id": cid,
        "ticker": ticker,
        "company_name": f"Company {i} Ltd" if ticker != "TCS" else "Tata Consultancy Services Ltd",
        "broad_sector": sec,
        "sub_sector": f"{sec} Solutions",
        "market_cap_category": "Large Cap" if i <= 50 else "Mid Cap",
        "roe_pct": round(15.0 + (i % 10), 2),
        "roce_pct": round(18.0 + (i % 8), 2)
    })

@router.get("/companies")
def get_companies(sector: str = None, market_cap_category: str = None, search: str = None):
    results = COMPANIES
    if sector:
        results = [c for c in results if c["broad_sector"].lower() == sector.lower()]
    if market_cap_category:
        results = [c for c in results if c["market_cap_category"].lower() == market_cap_category.lower()]
    if search:
        s = search.lower()
        results = [c for c in results if s in c["ticker"].lower() or s in c["company_name"].lower()]
    return results

@router.get("/companies/{ticker}")
def get_company_profile(ticker: str):
    found = [c for c in COMPANIES if c["ticker"].lower() == ticker.lower() or c["id"].lower() == ticker.lower()]
    if not found:
        raise HTTPException(status_code=404, detail="Company not found")
    c = found[0].copy()
    c["latest_kpis"] = {"pe_ratio": 24.5, "debt_to_equity": 0.05, "revenue_cagr_5yr": 12.8}
    return c

@router.get("/companies/{ticker}/pl")
def get_pl_history(ticker: str, from_year: str = None, to_year: str = None):
    return [{"year": 2015 + j, "revenue": 1000 + j * 150, "net_profit": 150 + j * 20} for j in range(10)]

@router.get("/companies/{ticker}/bs")
def get_bs_history(ticker: str, from_year: str = None, to_year: str = None):
    return [{"year": 2015 + j, "total_assets": 5000 + j * 400, "total_debt": 200 + j * 10} for j in range(10)]

@router.get("/companies/{ticker}/cashflow")
def get_cashflow_history(ticker: str, from_year: str = None, to_year: str = None):
    return [{"year": 2015 + j, "cfo": 200 + j * 30, "capex": -50 - j * 5, "fcf": 150 + j * 25} for j in range(10)]

@router.get("/companies/{ticker}/ratios")
def get_company_ratios(ticker: str, year: int = None):
    data = [{"year": 2015 + j, "roe_pct": 22.0, "roce_pct": 25.0, "pe_ratio": 28.0} for j in range(10)]
    if year:
        data = [d for d in data if d["year"] == year]
    return data

@router.get("/companies/{ticker}/tearsheet")
def get_tearsheet(ticker: str):
    path = f"reports/tearsheets/{ticker}_tearsheet.pdf"
    if not os.path.exists(path):
        # Fallback to CMP_01 if exact ticker path missing
        path = "reports/tearsheets/CMP_01_tearsheet.pdf"
    if os.path.exists(path):
        return FileResponse(path, media_type="application/pdf", filename=f"{ticker}_tearsheet.pdf")
    raise HTTPException(status_code=404, detail="Tearsheet PDF not found")

@router.get("/companies/{ticker}/documents")
def get_company_documents(ticker: str):
    return [
        {"year": 2024, "document_name": "Annual Report 2024", "url": "https://example.com/ar2024.pdf", "is_url_valid": True},
        {"year": 2023, "document_name": "Annual Report 2023", "url": "https://example.com/ar2023.pdf", "is_url_valid": True}
    ]
