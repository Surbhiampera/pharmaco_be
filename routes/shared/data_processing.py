"""
Shared data processing utilities for route modules.
Contains functions for data manipulation, validation, and processing.
"""

import io
from datetime import datetime
from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
from fastapi import HTTPException

# Import the AI signal detector
from ai_signal_detector import AISignalDetector

# Internal canonical names
CANON_DRUG = "drug_name"
CANON_EVENT = "adverse_event"

# FAERS column mapping
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


def read_csv(file_bytes: bytes) -> pd.DataFrame:
    """Read CSV from bytes with error handling."""
    buffer = io.BytesIO(file_bytes)
    try:
        df = pd.read_csv(buffer, low_memory=False)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Failed to parse CSV: {exc}")
    if df.empty:
        raise HTTPException(status_code=400, detail="Uploaded CSV is empty.")
    return df


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize and validate DataFrame columns."""
    df = df.copy()
    df.columns = df.columns.str.lower()

    # Validate presence of minimally required columns (accept aliases)
    has_drug = any(col in df.columns for col in REQUIRES_ANY_OF["drug"])
    has_event = any(col in df.columns for col in REQUIRES_ANY_OF["event"])
    if not (has_drug and has_event):
        missing = []
        if not has_drug:
            missing.append(REQUIRES_ANY_OF["drug"])
        if not has_event:
            missing.append(REQUIRES_ANY_OF["event"])
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Missing required columns.",
                "expect_any_of": missing,
            },
        )

    # Map to canonical names
    for source_col, canon in FAERS_COLUMN_MAP.items():
        if source_col in df.columns:
            df[canon] = df[source_col]

    # Types and parsing
    for date_col in ["fda_dt", "start_dt", "end_dt"]:
        if date_col in df.columns:
            # handle yyyymmdd or other string formats gracefully
            parsed = pd.to_datetime(
                df[date_col].astype(str), format="%Y%m%d", errors="coerce"
            )
            # Fallback general parse if all NaT
            if parsed.isna().all():
                parsed = pd.to_datetime(df[date_col], errors="coerce")
            df[date_col] = parsed

    for col in ["age", "dur"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # Ensure required canonical columns exist
    for col in [CANON_DRUG, CANON_EVENT, "outcome", "sex", "country", "dur_cod"]:
        if col not in df.columns:
            df[col] = "missing"

    return df


def compute_contingency(df: pd.DataFrame) -> pd.DataFrame:
    """Compute contingency table for drug-event pairs."""
    # a: reports with drug and event
    contingency = df.groupby([CANON_DRUG, CANON_EVENT]).size().reset_index(name="a")
    total_drug = df.groupby(CANON_DRUG).size().reset_index(name="drug_total")
    total_event = df.groupby(CANON_EVENT).size().reset_index(name="event_total")
    total = len(df)

    out = contingency.merge(total_drug, on=CANON_DRUG)
    out = out.merge(total_event, on=CANON_EVENT)
    out["b"] = out["drug_total"] - out["a"]
    out["c"] = out["event_total"] - out["a"]
    out["d"] = total - (out["a"] + out["b"] + out["c"])  # remaining
    # Guard against negatives due to any inconsistencies
    for col in ["a", "b", "c", "d"]:
        out[col] = out[col].clip(lower=0)
    return out[[CANON_DRUG, CANON_EVENT, "a", "b", "c", "d"]]


def compute_prr_ror_ic(cont: pd.DataFrame) -> pd.DataFrame:
    """Compute PRR, ROR, IC and confidence intervals."""
    df = cont.copy()
    eps = 1e-6
    # PRR
    df["PRR"] = (df["a"] / (df["a"] + df["b"] + eps)) / (
        (df["c"] / (df["c"] + df["d"] + eps)) + eps
    )
    # ROR
    df["ROR"] = (df["a"] / (df["b"] + eps)) / ((df["c"] / (df["d"] + eps)) + eps)
    # IC (observed/expected)
    n = (df["a"] + df["b"] + df["c"] + df["d"]).astype(float)
    expected = (df["a"] + df["b"]) * (df["a"] + df["c"]) / n.clip(lower=eps)
    df["IC"] = np.log2((df["a"].astype(float) + eps) / (expected + eps))

    # 95% CI lower bounds
    # PRR CI on log scale
    se_log_prr = np.sqrt(
        (1.0 / (df["a"] + eps))
        - (1.0 / (df["a"] + df["b"] + eps))
        + (1.0 / (df["c"] + eps))
        - (1.0 / (df["c"] + df["d"] + eps))
    )
    df["PRR_LCL"] = np.exp(np.log(df["PRR"] + eps) - 1.96 * se_log_prr)

    # ROR CI on log scale
    se_log_ror = np.sqrt(
        (1.0 / (df["a"] + eps))
        + (1.0 / (df["b"] + eps))
        + (1.0 / (df["c"] + eps))
        + (1.0 / (df["d"] + eps))
    )
    df["ROR_LCL"] = np.exp(np.log(df["ROR"] + eps) - 1.96 * se_log_ror)

    # Set PRR, ROR, IC to NaN if a < 3 (or your chosen threshold)
    min_count = 3
    mask = df["a"] < min_count
    df.loc[mask, ["PRR", "ROR", "IC", "PRR_LCL", "ROR_LCL"]] = np.nan

    # Flags
    df["meets_signal"] = (
        (df["PRR"] >= 2.0) & (df["a"] >= min_count) & (df["PRR_LCL"] > 1.0)
    ).astype(int)

    return df


def severity_score(series: pd.Series) -> pd.Series:
    """Map FAERS outcome codes to severity 1-5."""
    mapping = {
        "DE": 5,  # Death
        "LT": 5,  # Life Threatening
        "HO": 4,  # Hospitalization
        "DS": 4,  # Disability
        "CA": 4,  # Congenital Anomaly
        "RI": 3,  # Required Intervention
        "OT": 1,  # Other
    }
    return series.astype(str).str.upper().map(mapping).fillna(1).astype(int)


def jsonify_df(df: pd.DataFrame, orient: str = "records") -> List[Dict[str, Any]]:
    """Ensure JSON serializable (convert Timestamps and numpy types)."""
    converted = df.copy()
    for col in converted.columns:
        if np.issubdtype(converted[col].dtype, np.datetime64):
            converted[col] = (
                converted[col].astype("datetime64[ns]").dt.strftime("%Y-%m-%d")
            )
    return converted.to_dict(orient=orient)
