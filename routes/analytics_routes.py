"""
Analytics and visualization routes.
Handles data analysis and visualization endpoints.
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from typing import Dict, Any
import numpy as np

from .shared.cache_utils import ensure_uploaded, CACHE
from .shared.data_processing import jsonify_df, CANON_DRUG, CANON_EVENT

router = APIRouter(prefix="/analytics", tags=["Analytics & Visualization"])


@router.get("/distribution-analysis")
def distribution_analysis() -> Dict[str, Any]:
    """Get distribution analysis of the dataset."""
    ensure_uploaded()
    df = CACHE.raw_df
    # Age histogram (0-100 by decade)
    ages = df["age"].clip(lower=0, upper=100)
    bins = list(range(0, 110, 10))
    hist, edges = np.histogram(ages, bins=bins)
    sex_counts = df["sex"].astype(str).str.upper().value_counts().to_dict()
    country_top = df["country"].astype(str).value_counts().head(10).to_dict()
    return {
        "age_histogram": {
            "bins": list(map(int, edges[:-1])),
            "counts": list(map(int, hist)),
        },
        "sex_distribution": sex_counts,
        "top_countries": country_top,
    }


@router.get("/temporal-trends")
def temporal_trends() -> Dict[str, Any]:
    """Get temporal trends in the data."""
    ensure_uploaded()
    df = CACHE.raw_df.copy()
    if "fda_dt" not in df.columns:
        return {"trends": []}
    df["fda_month"] = df["fda_dt"].dt.to_period("M").dt.to_timestamp()
    trends = df.groupby("fda_month").size().reset_index(name="count")
    return {"trends": jsonify_df(trends.rename(columns={"fda_month": "month"}))}


@router.get("/risk-heatmaps")
def risk_heatmaps(limit_drugs: int = 20, limit_events: int = 20) -> Dict[str, Any]:
    """Get risk heatmaps for drugs and events."""
    ensure_uploaded()
    stats = CACHE.stats
    # pick top drugs and events by signal frequency
    top_drugs = (
        stats.groupby(CANON_DRUG)["meets_signal"]
        .sum()
        .sort_values(ascending=False)
        .head(limit_drugs)
        .index
    )
    top_events = (
        stats.groupby(CANON_EVENT)["meets_signal"]
        .sum()
        .sort_values(ascending=False)
        .head(limit_events)
        .index
    )
    sub = stats[stats[CANON_DRUG].isin(top_drugs) & stats[CANON_EVENT].isin(top_events)]
    pivot = sub.pivot_table(
        index=CANON_DRUG, columns=CANON_EVENT, values="PRR", fill_value=0
    )
    data = {
        "rows": list(pivot.index),
        "cols": list(pivot.columns),
        "values": [[float(x) for x in row] for row in pivot.values],
    }
    return {"prr_heatmap": data}


@router.get("/top-drugs-detected")
def top_drugs_detected(limit: int = 10) -> Dict[str, Any]:
    """Get top drugs with detected signals."""
    ensure_uploaded()
    df = CACHE.stats[CACHE.stats["meets_signal"] == 1]
    top = (
        df.groupby(CANON_DRUG)
        .size()
        .reset_index(name="signals")
        .sort_values("signals", ascending=False)
        .head(limit)
    )
    return {"top_drugs_detected": jsonify_df(top)}


@router.get("/most-frequent-adverse-events")
def most_frequent_adverse_events(limit: int = 10) -> Dict[str, Any]:
    """Get most frequent adverse events."""
    ensure_uploaded()
    top = (
        CACHE.raw_df.groupby(CANON_EVENT)
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
        .head(limit)
    )
    return {"most_frequent_adverse_events": jsonify_df(top)}


@router.get("/signal-trends")
def signal_trends() -> Dict[str, Any]:
    """Get signal trends over time."""
    ensure_uploaded()
    df = CACHE.raw_df.copy()
    if "fda_dt" not in df.columns:
        return {"signal_trends": []}
    df["fda_month"] = df["fda_dt"].dt.to_period("M").dt.to_timestamp()
    # mark if record belongs to any signaled pair
    pairs = set(
        zip(
            CACHE.stats.loc[CACHE.stats["meets_signal"] == 1, CANON_DRUG],
            CACHE.stats.loc[CACHE.stats["meets_signal"] == 1, CANON_EVENT],
        )
    )
    df["is_signal_record"] = df[[CANON_DRUG, CANON_EVENT]].apply(
        lambda r: (r[CANON_DRUG], r[CANON_EVENT]) in pairs, axis=1
    )
    trend = (
        df.groupby("fda_month")["is_signal_record"]
        .mean()
        .reset_index(name="signal_rate")
    )
    return {"signal_trends": jsonify_df(trend.rename(columns={"fda_month": "month"}))}


@router.get("/drug-event-severity-heatmap")
def drug_event_severity_heatmap(
    limit_drugs: int = 50, limit_events: int = 50
) -> Dict[str, Any]:
    """Get drug-event severity heatmap."""
    ensure_uploaded()
    stats = CACHE.stats
    top_drugs = (
        stats.groupby(CANON_DRUG)["meets_signal"]
        .sum()
        .sort_values(ascending=False)
        .head(limit_drugs)
        .index
    )
    top_events = (
        stats.groupby(CANON_EVENT)["meets_signal"]
        .sum()
        .sort_values(ascending=False)
        .head(limit_events)
        .index
    )
    sub = stats[stats[CANON_DRUG].isin(top_drugs) & stats[CANON_EVENT].isin(top_events)]
    pivot = sub.pivot_table(
        index=CANON_DRUG, columns=CANON_EVENT, values="mean_severity", fill_value=0
    )
    data = {
        "rows": list(pivot.index),
        "cols": list(pivot.columns),
        "values": [[float(x) for x in row] for row in pivot.values],
    }
    return {"severity_heatmap": data}


@router.get("/temporal-patterns")
def temporal_patterns() -> Dict[str, Any]:
    """Get temporal patterns in the data."""
    ensure_uploaded()
    df = CACHE.raw_df.copy()
    if "fda_dt" not in df.columns:
        return {"temporal_patterns": []}
    df["fda_week"] = df["fda_dt"].dt.to_period("W").dt.start_time
    patt = df.groupby(["fda_week", "sex"]).size().reset_index(name="count")
    return {"temporal_patterns": jsonify_df(patt.rename(columns={"fda_week": "week"}))}
