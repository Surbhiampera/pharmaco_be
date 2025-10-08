"""
Risk assessment routes.
Handles risk assessment and management endpoints.
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from typing import Dict, Any, List

from .shared.cache_utils import ensure_uploaded, CACHE
from .shared.data_processing import jsonify_df, CANON_DRUG, CANON_EVENT

router = APIRouter(prefix="/risk", tags=["Risk Assessment"])


@router.get("/assessment")
def risk_assessment(limit: int = 50) -> Dict[str, Any]:
    """Get risk assessment for drug-event pairs."""
    ensure_uploaded()
    df = CACHE.stats.copy()
    df["risk_score"] = (
        (df["PRR"].fillna(0)).clip(lower=0) * 0.5
        + (df["ROR"].fillna(0)).clip(lower=0) * 0.5
        + (df["mean_severity"].fillna(0))
    )
    ranked = df.sort_values(
        ["meets_signal", "risk_score"], ascending=[False, False]
    ).head(limit)
    cols = [
        CANON_DRUG,
        CANON_EVENT,
        "a",
        "PRR",
        "ROR",
        "IC",
        "PRR_LCL",
        "ROR_LCL",
        "mean_severity",
        "meets_signal",
        "risk_score",
    ]
    return {"risk_ranking": jsonify_df(ranked[cols])}


@router.get("/quick-actions")
def quick_actions() -> Dict[str, Any]:
    """Get quick action suggestions based on the data."""
    ensure_uploaded()
    total = int(len(CACHE.raw_df))
    signals = int(CACHE.stats["meets_signal"].sum())
    high_risk = int(((CACHE.stats["PRR"] >= 5) | (CACHE.stats["ROR"] >= 5)).sum())
    actions: List[str] = []
    if high_risk > 0:
        actions.append(
            "Initiate immediate safety review for high-risk pairs (PRR/ROR ≥ 5)."
        )
    if signals > 50:
        actions.append("Prioritize top 20 signal pairs for medical assessment.")
    if total > 10000 and signals / max(total, 1) > 0.002:
        actions.append(
            "Increase surveillance frequency; elevated signal rate for large cohort."
        )
    if not actions:
        actions.append("No urgent actions; continue routine monitoring.")
    return {"suggestions": actions}


@router.get("/key-insights")
def key_insights() -> Dict[str, Any]:
    """Get key insights from the data analysis."""
    ensure_uploaded()
    total = int(len(CACHE.raw_df))
    pairs = int(len(CACHE.stats))
    signals = int(CACHE.stats["meets_signal"].sum())
    high_risk = int(((CACHE.stats["PRR"] >= 5) | (CACHE.stats["ROR"] >= 5)).sum())
    avg_sev = float(
        CACHE.stats.loc[CACHE.stats["meets_signal"] == 1, "mean_severity"].mean() or 0.0
    )
    return {
        "insights": {
            "total_reports": total,
            "total_pairs": pairs,
            "signals": signals,
            "high_risk_pairs": high_risk,
            "avg_severity_signals": avg_sev,
        }
    }
