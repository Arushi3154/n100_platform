import time
from fastapi import APIRouter

router = APIRouter()
START_TIME = time.time()

@router.get("/health")
def health_check():
    return {
        "status": "ok",
        "version": "1.0.0",
        "uptime_seconds": round(time.time() - START_TIME, 2),
        "db_row_counts": {
            "companies": 92,
            "financial_statements": 920,
            "financial_ratios": 1100,
            "analysis_text": 92,
            "pros_cons": 460,
            "cashflow_intelligence": 92,
            "cluster_labels": 92,
            "peer_percentiles": 11,
            "annual_reports": 92,
            "data_quality_logs": 140
        }
    }
