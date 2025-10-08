"""
Data upload and management routes.
Handles dataset upload and processing.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

from .shared.data_processing import read_csv
from .shared.cache_utils import prepare_cache, CACHE

router = APIRouter(prefix="/data", tags=["Data Management"])


@router.post("/upload")
async def upload_dataset(file: UploadFile = File(...)) -> JSONResponse:
    """
    Upload and process a dataset.
    
    Args:
        file: Uploaded CSV file
    
    Returns:
        JSONResponse with upload confirmation and dataset info
    """
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")
    
    content = await file.read()
    df = read_csv(content)
    prepare_cache(df)
    
    return JSONResponse(
        {
            "message": "Dataset uploaded and processed.",
            "rows": int(len(CACHE.raw_df) if CACHE.raw_df is not None else 0),
            "processed_at": CACHE.processed_at,
        }
    )
