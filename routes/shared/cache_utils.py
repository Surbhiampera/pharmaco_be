"""
Shared cache utilities for route modules.
Contains the global cache and related utilities.
"""

from typing import Dict, Any, List, Optional
import pandas as pd
from ai_signal_detector import AISignalDetector


class DataCache:
    """Global data cache for the application."""
    def __init__(self) -> None:
        self.raw_df: Optional[pd.DataFrame] = None
        self.processed_at: Optional[str] = None
        self.stats: Optional[pd.DataFrame] = None  # drug-event table with PRR, ROR, IC
        self.ai_predictions: Optional[pd.DataFrame] = None  # AI model predictions
        self.ai_detector: Optional[AISignalDetector] = None
        self.status: str = "idle"
        self.column_map: Dict[str, str] = {}


# Global cache instance
CACHE = DataCache()


def ensure_uploaded() -> None:
    """Ensure that data has been uploaded and processed."""
    if CACHE.raw_df is None or CACHE.stats is None:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=400, detail="No dataset uploaded or processed yet."
        )


def prepare_cache(df: pd.DataFrame) -> None:
    """Prepare and cache the processed dataset."""
    from datetime import datetime
    from .data_processing import normalize_columns, compute_contingency, compute_prr_ror_ic, severity_score
    
    CACHE.status = "processing"
    df = normalize_columns(df)
    # add severity
    df["severity"] = severity_score(
        df.get("outcome", pd.Series(index=df.index, dtype=str))
    )

    # contingency and stats
    cont = compute_contingency(df)
    stats = compute_prr_ror_ic(cont)

    # merge severity mean per pair
    from .data_processing import CANON_DRUG, CANON_EVENT
    sev = (
        df.groupby([CANON_DRUG, CANON_EVENT])["severity"]
        .mean()
        .reset_index(name="mean_severity")
    )
    stats = stats.merge(sev, on=[CANON_DRUG, CANON_EVENT], how="left")

    # Initialize AI detector and run predictions
    try:
        ai_detector = AISignalDetector()
        ai_detector.load_model()

        # Run AI predictions on the dataset
        ai_predictions = ai_detector.predict_many(df)

        # Merge AI predictions with stats
        present = set(ai_predictions.columns)
        agg_spec: Dict[str, str] = {}
        if "is_signal" in present:
            agg_spec["is_signal"] = "max"
        if "probability" in present:
            agg_spec["probability"] = "mean"
        if "PRR" in present:
            agg_spec["PRR"] = "first"
        if "ROR" in present:
            agg_spec["ROR"] = "first"
        if "is_disproportional_signal" in present:
            agg_spec["is_disproportional_signal"] = "max"

        if agg_spec:
            ai_stats = (
                ai_predictions.groupby([CANON_DRUG, CANON_EVENT])
                .agg(agg_spec)
                .reset_index()
            )
            # Merge AI predictions with statistical results
            stats = stats.merge(
                ai_stats, on=[CANON_DRUG, CANON_EVENT], how="left", suffixes=("", "_ai")
            )

            # Update signal detection to include AI predictions (only if columns exist)
            meets = stats["meets_signal"].astype(int)
            if "is_signal" in stats.columns:
                meets = (meets == 1) | (stats["is_signal"].fillna(0).astype(int) == 1)
                meets = meets.astype(int)
            if "is_disproportional_signal" in stats.columns:
                meets = (meets == 1) | (
                    stats["is_disproportional_signal"].fillna(0).astype(int) == 1
                )
                meets = meets.astype(int)
            stats["meets_signal"] = meets

        CACHE.ai_detector = ai_detector
        CACHE.ai_predictions = ai_predictions

    except Exception as e:
        print(f"AI model inference failed: {e}")
        # Continue with statistical analysis only
        CACHE.ai_detector = None
        CACHE.ai_predictions = None

    # cache
    CACHE.raw_df = df
    CACHE.stats = stats
    CACHE.processed_at = datetime.utcnow().isoformat()
    CACHE.status = "ready"
