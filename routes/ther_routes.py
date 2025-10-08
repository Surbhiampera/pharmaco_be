"""
Routes for THER.csv file validation.
Handles single file, multiple files, folder, and ZIP uploads for THER files.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
from typing import List, Optional
import os
import zipfile
import io

from .validation_utils import (
    validate_single_file, 
    validate_multiple_files, 
    extract_files_from_zip,
    create_validation_summary
)
from .validation_models import THER_SCHEMA

router = APIRouter(prefix="/ther", tags=["THER File Validation"])


@router.post("/validate-single")
async def validate_single_ther_file(file: UploadFile = File(...)) -> JSONResponse:
    """
    Validate a single THER.csv file.
    
    Args:
        file: Uploaded CSV file
    
    Returns:
        JSONResponse with validation results
    """
    if not file.filename.lower().endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")
    
    file_bytes = await file.read()
    result = validate_single_file(file_bytes, file.filename, THER_SCHEMA)
    
    if result.is_valid:
        return JSONResponse({
            "status": "success",
            "message": "File validation passed",
            "file_name": result.file_name,
            "total_rows": result.total_rows,
            "valid_rows": result.valid_rows
        })
    else:
        return JSONResponse({
            "status": "error",
            "message": "File validation failed",
            "file_name": result.file_name,
            "errors": [{"field": e.field, "message": e.message} for e in result.errors]
        }, status_code=400)


@router.post("/validate-multiple")
async def validate_multiple_ther_files(files: List[UploadFile] = File(...)) -> JSONResponse:
    """
    Validate multiple THER.csv files.
    
    Args:
        files: List of uploaded CSV files
    
    Returns:
        JSONResponse with validation results for all files
    """
    # Filter only CSV files
    csv_files = [f for f in files if f.filename.lower().endswith('.csv')]
    
    if not csv_files:
        raise HTTPException(status_code=400, detail="No CSV files provided")
    
    # Process each file
    file_data = []
    for file in csv_files:
        file_bytes = await file.read()
        file_data.append((file.filename, file_bytes))
    
    # Validate all files
    results = validate_multiple_files(file_data, THER_SCHEMA)
    summary = create_validation_summary(results)
    
    # Check if any files failed validation
    failed_files = [r for r in results if not r.is_valid]
    
    if failed_files:
        return JSONResponse({
            "status": "error",
            "message": f"{len(failed_files)} out of {len(results)} files failed validation",
            "summary": summary
        }, status_code=400)
    else:
        return JSONResponse({
            "status": "success",
            "message": "All files passed validation",
            "summary": summary
        })


@router.post("/validate-zip")
async def validate_ther_zip_file(file: UploadFile = File(...)) -> JSONResponse:
    """
    Validate THER.csv files from a ZIP archive.
    
    Args:
        file: Uploaded ZIP file containing CSV files
    
    Returns:
        JSONResponse with validation results
    """
    if not file.filename.lower().endswith('.zip'):
        raise HTTPException(status_code=400, detail="Only ZIP files are supported")
    
    try:
        zip_bytes = await file.read()
        files = extract_files_from_zip(zip_bytes)
        
        if not files:
            raise HTTPException(status_code=400, detail="No CSV files found in ZIP archive")
        
        # Validate all files
        results = validate_multiple_files(files, THER_SCHEMA)
        summary = create_validation_summary(results)
        
        # Check if any files failed validation
        failed_files = [r for r in results if not r.is_valid]
        
        if failed_files:
            return JSONResponse({
                "status": "error",
                "message": f"{len(failed_files)} out of {len(results)} files failed validation",
                "summary": summary
            }, status_code=400)
        else:
            return JSONResponse({
                "status": "success",
                "message": "All files in ZIP passed validation",
                "summary": summary
            })
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing ZIP file: {str(e)}")


@router.post("/validate-folder")
async def validate_ther_folder(files: List[UploadFile] = File(...)) -> JSONResponse:
    """
    Validate all THER.csv files from a folder upload.
    This endpoint accepts multiple files that would be uploaded from a folder.
    
    Args:
        files: List of uploaded files from folder
    
    Returns:
        JSONResponse with validation results
    """
    # Filter only CSV files
    csv_files = [f for f in files if f.filename.lower().endswith('.csv')]
    
    if not csv_files:
        raise HTTPException(status_code=400, detail="No CSV files provided")
    
    # Process each file
    file_data = []
    for file in csv_files:
        file_bytes = await file.read()
        file_data.append((file.filename, file_bytes))
    
    # Validate all files
    results = validate_multiple_files(file_data, THER_SCHEMA)
    summary = create_validation_summary(results)
    
    # Check if any files failed validation
    failed_files = [r for r in results if not r.is_valid]
    
    if failed_files:
        return JSONResponse({
            "status": "error",
            "message": f"{len(failed_files)} out of {len(results)} files failed validation",
            "summary": summary
        }, status_code=400)
    else:
        return JSONResponse({
            "status": "success",
            "message": "All files passed validation",
            "summary": summary
        })


@router.get("/schema")
async def get_ther_schema() -> JSONResponse:
    """
    Get the THER file schema requirements.
    
    Returns:
        JSONResponse with schema information
    """
    return JSONResponse({
        "file_prefix": THER_SCHEMA.file_prefix,
        "required_columns": THER_SCHEMA.required_columns,
        "column_types": THER_SCHEMA.column_types,
        "example_row": THER_SCHEMA.example_row
    })
