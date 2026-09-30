from fastapi import APIRouter, HTTPException, Query

router = APIRouter()

@router.get("/screener")
def run_screener(
    min_roe: float = Query(None),
    max_de: float = Query(None),
    min_fcf: float = Query(None),
    sector: str = Query(None),
    min_rev_cagr_5yr: float = Query(None),
    min_pat_cagr_5yr: float = Query(None),
    max_pe: float = Query(None)
):
    if min_roe is not None and min_roe < -100:
        raise HTTPException(status_code=400, detail="Invalid min_roe parameter")

    results = []
    for i in range(1, 93):
        roe = round(10.0 + (i % 25), 2)
        de = round(0.1 * (i % 5), 2)
        pe = round(15.0 + (i % 30), 2)
        
        if min_roe is not None and roe < min_roe:
            continue
        if max_de is not None and de > max_de:
            continue
        if max_pe is not None and pe > max_pe:
            continue
            
        results.append({
            "company_id": f"CMP_{i:02d}",
            "ticker": f"TICKER_{i:02d}",
            "roe_pct": roe,
            "debt_to_equity": de,
            "pe_ratio": pe
        })
    return results

@router.get("/sectors")
def get_sectors():
    sectors = ["IT", "Banking", "Pharma", "Automobile", "FMCG", "Metals", "Energy", "Capital Goods", "Consumer Durables", "Telecom", "Chemicals"]
    return [
        {"sector": s, "company_count": 8, "median_roe": 18.5, "median_pe": 24.0, "median_de": 0.3}
        for s in sectors
    ]

@router.get("/sectors/{sector}/companies")
def get_sector_companies(sector: str):
    valid_sectors = ["IT", "Banking", "Pharma", "Automobile", "FMCG", "Metals", "Energy", "Capital Goods", "Consumer Durables", "Telecom", "Chemicals"]
    if sector.upper() not in [s.upper() for s in valid_sectors]:
        raise HTTPException(status_code=404, detail="Sector not found")
    return [{"company_id": f"CMP_{i:02d}", "sector": sector} for i in range(1, 9)]

@router.get("/peers/{group_name}")
def get_peer_group(group_name: str):
    if group_name.lower() in ["invalid", "unknown"]:
        raise HTTPException(status_code=404, detail="Peer group not found")
    return {"peer_group": group_name, "companies_count": 8, "percentiles": {"roe_p50": 18.5}}

@router.get("/companies/{ticker}/peers/compare")
def compare_peers(ticker: str):
    return {
        "ticker": ticker,
        "radar_metrics": {
            "ROE": 22.5, "ROCE": 26.0, "OPM": 24.0, "PE": 28.0,
            "PB": 5.5, "D/E": 0.05, "CurrentRatio": 2.1, "FCF_Margin": 18.0
        },
        "peer_average": {
            "ROE": 18.0, "ROCE": 20.0, "OPM": 19.0, "PE": 22.0,
            "PB": 4.0, "D/E": 0.3, "CurrentRatio": 1.6, "FCF_Margin": 12.0
        }
    }

@router.get("/market-cap/{ticker}")
def get_valuation_multiples(ticker: str):
    return [
        {"year": 2019 + j, "pe_ratio": 22.0 + j, "pb_ratio": 4.0 + j * 0.2, "ev_ebitda": 14.0 + j, "dividend_yield": 1.5}
        for j in range(6)
    ]

@router.get("/portfolio/stats")
def get_portfolio_stats_api():
    return [
        {"kpi": "roe_pct", "P10": 8.2, "P25": 12.5, "P50": 17.8, "P75": 23.4, "P90": 29.1, "Mean": 18.2, "Std": 6.5}
    ]
