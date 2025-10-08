from __future__ import annotations

import io
from datetime import datetime
from typing import Dict, Any, List, Optional

import numpy as np
import pandas as pd
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Import the AI signal detector
from ai_signal_detector import AISignalDetector
from dotenv import load_dotenv
import os

# Import all route modules
from routes import (
    demo_routes, drug_routes, indi_routes, outc_routes, reac_routes, rpsr_routes, ther_routes,
    data_routes, stats_routes, signal_routes, ai_routes, analytics_routes, risk_routes, distribution_routes
)

load_dotenv()

app = FastAPI(title="FAERS Signal Detection API", version="2.0.0")

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS")
origins = [
    "http://localhost:8080",
    "http://localhost:4173",
    ALLOWED_ORIGINS
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,  # Allow cookies, authorization headers, etc.
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Include all route modules
# Validation routes
app.include_router(demo_routes.router)
app.include_router(drug_routes.router)
app.include_router(indi_routes.router)
app.include_router(outc_routes.router)
app.include_router(reac_routes.router)
app.include_router(rpsr_routes.router)
app.include_router(ther_routes.router)

# Main application routes
app.include_router(data_routes.router)
app.include_router(stats_routes.router)
app.include_router(signal_routes.router)
app.include_router(ai_routes.router)
app.include_router(analytics_routes.router)
app.include_router(risk_routes.router)
app.include_router(distribution_routes.router)

# ------------------------------ Global State ------------------------------


class DataCache:
    def __init__(self) -> None:
        self.raw_df: Optional[pd.DataFrame] = None
        self.processed_at: Optional[str] = None
        self.stats: Optional[pd.DataFrame] = None  # drug-event table with PRR, ROR, IC
        self.ai_predictions: Optional[pd.DataFrame] = None  # AI model predictions
        self.ai_detector: Optional[AISignalDetector] = None
        self.status: str = "idle"
        self.column_map: Dict[str, str] = {}


CACHE = DataCache()


# ------------------------------ Column Schema ------------------------------


EXPECTED_COLUMNS = [
    "primaryid",
    "caseid",
    "caseversion",
    "fda_dt",
    "age",
    "sex",
    "rpt_country",
    "rpsr_cod",
    "drug_seq",
    "role_cod",
    "drugname",
    "prod_ai",
    "pt",
    "outc_cod",
    "indi_drug_seq",
    "indi_pt",
    "rpsr_cod",
    "start_dt",
    "end_dt",
    "dur",
    "dur_cod",
]

# Internal canonical names
CANON_DRUG = "drug_name"
CANON_EVENT = "adverse_event"

FAERS_COLUMN_MAP = {
    # FAERS originals -> canonical
    "drugname": CANON_DRUG,
    "prod_ai": "prod_ai",
    "pt": CANON_EVENT,
    "indi_pt": "indication",
    "indi_drug_seq": "indi_drug_seq",
    "age": "age",
    "sex": "sex",
    "outc_cod": "outcome",
    "rpt_country": "country",
    "role_cod": "role_cod",
    "dur_cod": "dur_cod",
    "dur": "dur",
    "fda_dt": "fda_dt",
    "caseid": "case_id",
    "caseversion": "case_version",
    "primaryid": "primary_id",
    "drug_seq": "drug_sequence",
    "start_dt": "start_dt",
    "end_dt": "end_dt",
    # Alternate headers from provided CSV -> canonical
    "drug_name": CANON_DRUG,
    "adverse_event": CANON_EVENT,
    "active_ingredient": "prod_ai",
    "indication_sequence": "indi_drug_seq",
    "fda_date": "fda_dt",
    "start_date": "start_dt",
    "end_date": "end_dt",
}

# Minimum required source columns to proceed (either FAERS or canonical)
REQUIRES_ANY_OF = {
    "drug": ["drugname", "drug_name"],
    "event": ["pt", "adverse_event"],
}


# All utility functions have been moved to shared modules


# All API endpoints have been moved to separate route modules


# ------------------------------ Run (optional) ------------------------------

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app_v2:app", host="0.0.0.0", port=8000, reload=False)
