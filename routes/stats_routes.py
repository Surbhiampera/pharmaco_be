"""
Basic statistics routes.
Handles basic statistical information about the dataset.
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from typing import Dict, Any

from .shared.cache_utils import ensure_uploaded, CACHE

router = APIRouter(prefix="/stats", tags=["Basic Statistics"])


@router.get("/total-reports")
def total_reports() -> Dict[str, Any]:
    """Get total number of reports in the dataset."""
    ensure_uploaded()
    return {"total_reports": int(len(CACHE.raw_df))}


@router.get("/detected-signals")
def detected_signals() -> Dict[str, Any]:
    """Get count of detected signals."""
    ensure_uploaded()
    count = int(CACHE.stats["meets_signal"].sum())
    return {"detected_signals": count}


@router.get("/critical-signals")
def critical_signals() -> Dict[str, Any]:
    """Get count of critical signals (severity >= 5)."""
    ensure_uploaded()
    df = CACHE.raw_df
    stats = CACHE.stats
    from .shared.data_processing import CANON_DRUG, CANON_EVENT
    
    sev = (
        df.groupby([CANON_DRUG, CANON_EVENT])["severity"]
        .max()
        .reset_index(name="max_severity")
    )
    merged = stats.merge(sev, on=[CANON_DRUG, CANON_EVENT], how="left")
    crit = merged[(merged["meets_signal"] == 1) & (merged["max_severity"] >= 5)]
    return {"critical_signals": int(len(crit))}


@router.get("/high-risk")
def high_risk() -> Dict[str, Any]:
    """Get count of high-risk pairs (PRR >= 5 or ROR >= 5)."""
    ensure_uploaded()
    hr = CACHE.stats[(CACHE.stats["PRR"] >= 5) | (CACHE.stats["ROR"] >= 5)]
    return {"high_risk_pairs": int(len(hr))}


@router.get("/signal-rate")
def signal_rate() -> Dict[str, Any]:
    """Get signal rate (proportion of pairs that are signals)."""
    ensure_uploaded()
    rate = float(CACHE.stats["meets_signal"].mean()) if len(CACHE.stats) else 0.0
    return {"signal_rate": rate}


@router.get("/total-signal-pairs")
def total_signal_pairs() -> Dict[str, Any]:
    """Get total number of signal pairs."""
    ensure_uploaded()
    return {"total_signal_pairs": int(CACHE.stats["meets_signal"].sum())}


@router.get("/average-severity")
def average_severity() -> Dict[str, Any]:
    """Get average severity of signal pairs."""
    ensure_uploaded()
    df = CACHE.stats[CACHE.stats["meets_signal"] == 1]
    avg = float(df["mean_severity"].mean()) if len(df) else 0.0
    return {"average_severity": avg}


@router.get("/system-status")
def system_status() -> Dict[str, Any]:
    """Get system status and readiness information."""
    ready = CACHE.raw_df is not None and CACHE.stats is not None
    ai_ready = CACHE.ai_detector is not None and CACHE.ai_predictions is not None

    return {
        "status": CACHE.status,
        "ready": ready,
        "ai_model_ready": ai_ready,
        "processed_at": CACHE.processed_at,
        "total_reports": int(len(CACHE.raw_df)) if CACHE.raw_df is not None else 0,
        "signal_pairs": (
            int(CACHE.stats["meets_signal"].sum()) if CACHE.stats is not None else 0
        ),
        "ai_signal_pairs": (
            int(CACHE.ai_predictions["is_signal"].sum())
            if CACHE.ai_predictions is not None
            and "is_signal" in CACHE.ai_predictions.columns
            else 0
        ),
    }
