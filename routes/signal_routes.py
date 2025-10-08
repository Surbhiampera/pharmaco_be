"""
Signal analysis routes.
Handles signal detection and analysis endpoints.
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional

from .shared.cache_utils import ensure_uploaded, CACHE
from .shared.data_processing import jsonify_df, CANON_DRUG, CANON_EVENT

router = APIRouter(prefix="/signals", tags=["Signal Analysis"])


@router.get("/top-drugs-signals")
def top_drugs_signals(limit: int = 10) -> Dict[str, Any]:
    """Get top drugs with the most signals."""
    ensure_uploaded()
    df = CACHE.stats[CACHE.stats["meets_signal"] == 1]
    top = (
        df.groupby(CANON_DRUG)
        .size()
        .reset_index(name="signal_count")
        .sort_values("signal_count", ascending=False)
        .head(limit)
    )
    return {"top_drugs": jsonify_df(top)}


@router.get("/top-adverse-events")
def top_adverse_events(limit: int = 10) -> Dict[str, Any]:
    """Get top adverse events with the most signals."""
    ensure_uploaded()
    df = CACHE.stats[CACHE.stats["meets_signal"] == 1]
    top = (
        df.groupby(CANON_EVENT)
        .size()
        .reset_index(name="signal_count")
        .sort_values("signal_count", ascending=False)
        .head(limit)
    )
    return {"top_adverse_events": jsonify_df(top)}


@router.get("/drug-event-signal-pairs")
def drug_event_signal_pairs(limit: Optional[int] = None) -> Dict[str, Any]:
    """Get drug-event signal pairs with details."""
    ensure_uploaded()
    cols = [CANON_DRUG, CANON_EVENT, "a", "PRR", "ROR", "IC", "mean_severity"]
    # Only include pairs with a >= 3
    df = CACHE.stats[(CACHE.stats["meets_signal"] == 1) & (CACHE.stats["a"] >= 3)][cols].sort_values("PRR", ascending=False)
    if limit is None:
        limit = len(df)
    df = df.head(limit)
    return {"signal_pairs": jsonify_df(df)}


@router.get("/statistical-measures")
def statistical_measures(limit: int = 100) -> Dict[str, Any]:
    """Get statistical measures for drug-event pairs."""
    ensure_uploaded()
    cols = [
        CANON_DRUG,
        CANON_EVENT,
        "a",
        "b",
        "c",
        "d",
        "PRR",
        "ROR",
        "IC",
        "PRR_LCL",
        "ROR_LCL",
        "meets_signal",
    ]
    return {"measures": jsonify_df(CACHE.stats[cols].head(limit))}
