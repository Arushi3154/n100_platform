import json
import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from src.api.routers import health, companies, screener

app = FastAPI(
    title="Nifty 100 Financial Platform API",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/api/v1/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    print(f"[API Log] {request.method} {request.url.path} - Completed in {duration:.4f}s with status {response.status_code}")
    return response

app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(companies.router, prefix="/api/v1", tags=["Companies"])
app.include_router(screener.router, prefix="/api/v1", tags=["Screener & Analytics"])

def export_openapi_spec():
    import os
    os.makedirs("docs", exist_ok=True)
    with open("docs/openapi.json", "w") as f:
        json.dump(app.openapi(), f, indent=2)
    print("[API] Exported OpenAPI Spec -> docs/openapi.json")

if __name__ == "__main__":
    export_openapi_spec()
