"""
Signal distribution routes.
Handles signal distribution and criteria endpoints.
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from typing import Dict, Any

from .shared.cache_utils import ensure_uploaded, CACHE
from .shared.data_processing import jsonify_df, CANON_DRUG, CANON_EVENT

router = APIRouter(prefix="/distribution", tags=["Signal Distribution"])


@router.get("/signal-distribution")
def signal_distribution() -> Dict[str, Any]:
    """Get signal distribution by drug and event."""
    ensure_uploaded()
    stats = CACHE.stats
    by_drug = (
        stats.groupby(CANON_DRUG)["meets_signal"]
        .sum()
        .reset_index(name="signals")
        .sort_values("signals", ascending=False)
    )
    by_event = (
        stats.groupby(CANON_EVENT)["meets_signal"]
        .sum()
        .reset_index(name="signals")
        .sort_values("signals", ascending=False)
    )
    return {
        "by_drug": jsonify_df(by_drug.head(50)),
        "by_event": jsonify_df(by_event.head(50)),
    }


@router.get("/signal-criteria")
def signal_criteria() -> Dict[str, Any]:
    """Get signal detection criteria."""
    return {
        "criteria": {
            "PRR_threshold": 2.0,
            "minimum_frequency_a": 3,
            "lower_CI_PRR_gt": 1.0,
        }
    }
