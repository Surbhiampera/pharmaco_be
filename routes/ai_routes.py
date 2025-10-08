"""
AI model routes.
Handles AI model predictions and analysis.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional
import pandas as pd
from datetime import datetime

from .shared.cache_utils import ensure_uploaded, CACHE
from .shared.data_processing import jsonify_df, CANON_DRUG, CANON_EVENT

router = APIRouter(prefix="/ai", tags=["AI Model"])


@router.get("/signals")
def ai_signals(limit: int = 100) -> Dict[str, Any]:
    """Get signals detected by AI model only."""
    ensure_uploaded()
    if CACHE.ai_predictions is None:
        return {"ai_signals": [], "message": "AI model not available"}

    df_ai = CACHE.ai_predictions
    if "is_signal" not in df_ai.columns:
        return {"ai_signals": [], "message": "AI signals not provided by model"}

    ai_signals_df = df_ai[df_ai["is_signal"] == 1]
    cols = [CANON_DRUG, CANON_EVENT]
    for c in ["probability", "PRR", "ROR", "is_disproportional_signal"]:
        if c in ai_signals_df.columns:
            cols.append(c)
    result = ai_signals_df[cols]
    sort_key = "probability" if "probability" in result.columns else None
    if sort_key:
        result = result.sort_values(sort_key, ascending=False)
    result = result.head(limit)
    return {"ai_signals": jsonify_df(result)}


@router.get("/signal-count")
def ai_signal_count() -> Dict[str, Any]:
    """Get count of signals detected by AI model."""
    ensure_uploaded()
    if CACHE.ai_predictions is None or "is_signal" not in CACHE.ai_predictions.columns:
        return {"ai_signal_count": 0, "message": "AI signals not available"}

    count = int(CACHE.ai_predictions["is_signal"].sum())
    return {"ai_signal_count": count}


@router.get("/high-confidence-signals")
def ai_high_confidence_signals(
    threshold: float = 0.8, limit: int = 50
) -> Dict[str, Any]:
    """Get AI signals with high confidence (probability >= threshold)."""
    ensure_uploaded()
    if CACHE.ai_predictions is None:
        return {"high_confidence_signals": [], "message": "AI model not available"}

    if "is_signal" not in CACHE.ai_predictions.columns:
        return {"high_confidence_signals": [], "message": "AI signals not available"}

    if "probability" not in CACHE.ai_predictions.columns:
        return {"high_confidence_signals": [], "message": "Probability not available"}

    high_conf = CACHE.ai_predictions[
        (CACHE.ai_predictions["is_signal"] == 1)
        & (CACHE.ai_predictions["probability"] >= threshold)
    ]
    cols = [CANON_DRUG, CANON_EVENT, "probability"]
    for c in ["PRR", "ROR"]:
        if c in high_conf.columns:
            cols.append(c)
    result = high_conf[cols].sort_values("probability", ascending=False).head(limit)
    return {"high_confidence_signals": jsonify_df(result)}


@router.get("/model-status")
def ai_model_status() -> Dict[str, Any]:
    """Check if AI model is loaded and available."""
    ensure_uploaded()
    return {
        "ai_model_available": CACHE.ai_detector is not None,
        "ai_predictions_available": CACHE.ai_predictions is not None,
        "total_ai_predictions": (
            len(CACHE.ai_predictions) if CACHE.ai_predictions is not None else 0
        ),
    }


@router.get("/hybrid-signals")
def hybrid_signals(limit: int = 100) -> Dict[str, Any]:
    """Get signals detected by both statistical and AI methods."""
    ensure_uploaded()
    if CACHE.ai_predictions is None:
        return {"hybrid_signals": [], "message": "AI model not available"}

    if "is_signal" not in CACHE.ai_predictions.columns:
        return {"hybrid_signals": [], "message": "AI signals not available"}

    # Find pairs that are signals by both methods
    ai_pairs = set(
        zip(
            CACHE.ai_predictions[CACHE.ai_predictions["is_signal"] == 1][CANON_DRUG],
            CACHE.ai_predictions[CACHE.ai_predictions["is_signal"] == 1][CANON_EVENT],
        )
    )

    stat_pairs = set(
        zip(
            CACHE.stats[CACHE.stats["meets_signal"] == 1][CANON_DRUG],
            CACHE.stats[CACHE.stats["meets_signal"] == 1][CANON_EVENT],
        )
    )

    hybrid_pairs = ai_pairs.intersection(stat_pairs)

    if not hybrid_pairs:
        return {"hybrid_signals": [], "message": "No signals detected by both methods"}

    # Get details for hybrid signals
    hybrid_df = CACHE.stats[
        CACHE.stats[[CANON_DRUG, CANON_EVENT]].apply(
            lambda x: (x[CANON_DRUG], x[CANON_EVENT]) in hybrid_pairs, axis=1
        )
    ]

    cols = [
        CANON_DRUG,
        CANON_EVENT,
        "a",
        "PRR",
        "ROR",
        "IC",
        "mean_severity",
        "meets_signal",
    ]
    result = hybrid_df[cols].sort_values("PRR", ascending=False).head(limit)
    return {"hybrid_signals": jsonify_df(result)}


@router.get("/prediction-distribution")
def ai_prediction_distribution() -> Dict[str, Any]:
    """Get distribution of AI prediction probabilities."""
    ensure_uploaded()
    if CACHE.ai_predictions is None:
        return {"distribution": [], "message": "AI model not available"}

    if "probability" not in CACHE.ai_predictions.columns:
        return {"distribution": [], "message": "Probability not available"}

    # Create probability bins
    import numpy as np
    probs = CACHE.ai_predictions["probability"]
    bins = [0, 0.2, 0.4, 0.6, 0.8, 1.0]
    hist, edges = np.histogram(probs, bins=bins)

    return {
        "distribution": {
            "bins": [f"{edges[i]:.1f}-{edges[i+1]:.1f}" for i in range(len(edges) - 1)],
            "counts": [int(x) for x in hist],
        }
    }


@router.post("/predict-single")
async def predict_single(
    drug_name: str,
    adverse_event: str,
    age: int = 50,
    sex: str = "F",
    country: str = "US",
    outcome: str = "OT",
    indication: str = "Unknown",
) -> Dict[str, Any]:
    """Predict signal for a single drug-event pair using AI model."""
    if CACHE.ai_detector is None:
        raise HTTPException(
            status_code=400, detail="AI model not available. Upload dataset first."
        )

    # Create single record DataFrame
    single_record = pd.DataFrame(
        [
            {
                "drug_name": drug_name,
                "adverse_event": adverse_event,
                "age": age,
                "sex": sex,
                "country": country,
                "outcome": outcome,
                "indication": indication,
                "fda_dt": datetime.now().strftime("%Y%m%d"),
                "dur": 30,
                "dur_cod": "DY",
            }
        ]
    )

    try:
        # Use AI detector for prediction
        result = CACHE.ai_detector.predict_many(single_record)
        prediction = result.iloc[0]

        return {
            "drug_name": drug_name,
            "adverse_event": adverse_event,
            "is_signal": bool(prediction.get("is_signal", False)),
            "probability": float(prediction.get("probability", 0.0)),
            "PRR": float(prediction.get("PRR", 1.0)),
            "ROR": float(prediction.get("ROR", 1.0)),
            "is_disproportional_signal": bool(
                prediction.get("is_disproportional_signal", False)
            ),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@router.get("/predicted-dataset")
def predicted_dataset(limit: Optional[int] = None) -> Dict[str, Any]:
    """Get the uploaded dataset with AI predictions (important columns only)."""
    ensure_uploaded()
    if CACHE.ai_detector is None or CACHE.raw_df is None:
        raise HTTPException(status_code=400, detail="AI model or dataset not available.")

    # Run predict_many if not already cached
    if CACHE.ai_predictions is None:
        CACHE.ai_predictions = CACHE.ai_detector.predict_many(CACHE.raw_df)

    df = CACHE.ai_predictions.copy()
    if limit is None:
        limit = len(df)
    important_cols = [
        CANON_DRUG,
        CANON_EVENT,
        "age",
        "sex",
        "country",
        "outcome",
        "indication",
        "dur",
        "dur_cod",
        "fda_dt",
        "is_signal",
        "probability",
        "PRR",
        "ROR",
        "is_disproportional_signal",
    ]
    # Only keep columns that exist
    cols = [c for c in important_cols if c in df.columns]
    result = df[cols].head(limit)
    return {"predicted_dataset": jsonify_df(result)}
