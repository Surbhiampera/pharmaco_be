"""
Shared validation utilities for CSV file validation.
Handles file name validation, column validation, and data type validation.
"""

import io
import zipfile
import os
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
from fastapi import HTTPException, UploadFile
from .validation_models import ValidationResult, ValidationError, SCHEMA_MAP, FileSchema
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def validate_file_name(file_name: str, expected_prefix: str) -> bool:
    """
    Validate that file name starts with the expected prefix.
    
    Args:
        file_name: Name of the file to validate
        expected_prefix: Expected prefix (e.g., "DEMO", "DRUG")
    
    Returns:
        bool: True if valid, False otherwise
    """
    if not file_name:
        return False
    
    # Remove extension and check prefix
    name_without_ext = os.path.splitext(file_name)[0]
    return name_without_ext.startswith(expected_prefix)


def validate_columns(df: pd.DataFrame, required_columns: List[str]) -> List[ValidationError]:
    """
    Validate that all required columns exist in the DataFrame.
    
    Args:
        df: DataFrame to validate
        required_columns: List of required column names
    
    Returns:
        List of validation errors (empty if all columns present)
    """
    errors = []
    df_columns = [col.lower() for col in df.columns]
    
    for col in required_columns:
        if col.lower() not in df_columns:
            errors.append(ValidationError(
                field=col,
                message=f"Required column '{col}' is missing"
            ))
    
    return errors


def validate_data_types(df: pd.DataFrame, column_types: Dict[str, str]) -> List[ValidationError]:
    """
    Validate data types for each column.
    
    Args:
        df: DataFrame to validate
        column_types: Dictionary mapping column names to expected types
    
    Returns:
        List of validation errors
    """
    errors = []
    
    for col, expected_type in column_types.items():
        if col.lower() not in [c.lower() for c in df.columns]:
            continue  # Skip if column doesn't exist (handled by column validation)
        
        # Get the actual column name (case-insensitive)
        actual_col = next(c for c in df.columns if c.lower() == col.lower())
        
        try:
            if expected_type == "integer":
                # Try to convert to numeric, check for non-numeric values
                numeric_series = pd.to_numeric(df[actual_col], errors='coerce')
                non_numeric_count = numeric_series.isna().sum()
                if non_numeric_count > 0:
                    errors.append(ValidationError(
                        field=col,
                        message=f"Column '{col}' contains {non_numeric_count} non-numeric values"
                    ))
            
            elif expected_type == "timestamp":
                # Try to parse as timestamp
                if df[actual_col].dtype == 'object':
                    # Try different timestamp formats
                    parsed = pd.to_datetime(df[actual_col], format='%Y%m%d', errors='coerce')
                    if parsed.isna().any():
                        # Try general parsing
                        parsed = pd.to_datetime(df[actual_col], errors='coerce')
                        invalid_count = parsed.isna().sum()
                        if invalid_count > 0:
                            errors.append(ValidationError(
                                field=col,
                                message=f"Column '{col}' contains {invalid_count} invalid timestamp values"
                            ))
            
            elif expected_type == "string":
                # String validation - check for null values that shouldn't be null
                null_count = df[actual_col].isna().sum()
                if null_count > 0:
                    errors.append(ValidationError(
                        field=col,
                        message=f"Column '{col}' contains {null_count} null values"
                    ))
        
        except Exception as e:
            errors.append(ValidationError(
                field=col,
                message=f"Error validating column '{col}': {str(e)}"
            ))
    
    return errors


def read_csv_from_bytes(file_bytes: bytes) -> pd.DataFrame:
    """
    Read CSV from bytes with error handling.
    
    Args:
        file_bytes: CSV file content as bytes
    
    Returns:
        DataFrame
    
    Raises:
        HTTPException: If CSV cannot be parsed
    """
    try:
        buffer = io.BytesIO(file_bytes)
        df = pd.read_csv(buffer, low_memory=False)
        if df.empty:
            raise HTTPException(status_code=400, detail="CSV file is empty")
        return df
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse CSV: {str(e)}")


def validate_single_file(file_bytes: bytes, file_name: str, schema: FileSchema) -> ValidationResult:
    """
    Validate a single CSV file against its schema.
    
    Args:
        file_bytes: File content as bytes
        file_name: Name of the file
        schema: Schema to validate against
    
    Returns:
        ValidationResult with validation status and errors
    """
    errors = []
    
    # Validate file name
    if not validate_file_name(file_name, schema.file_prefix):
        errors.append(ValidationError(
            field="file_name",
            message=f"File name must start with '{schema.file_prefix}'"
        ))
        return ValidationResult(
            is_valid=False,
            errors=errors,
            file_name=file_name,
            total_rows=0,
            valid_rows=0
        )
    
    try:
        # Read CSV
        df = read_csv_from_bytes(file_bytes)
        total_rows = len(df)
        
        # Validate columns
        column_errors = validate_columns(df, schema.required_columns)
        errors.extend(column_errors)
        
        # Validate data types (only if columns are correct)
        if not column_errors:
            type_errors = validate_data_types(df, schema.column_types)
            errors.extend(type_errors)
        
        valid_rows = total_rows - len([e for e in errors if e.row is not None])
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            file_name=file_name,
            total_rows=total_rows,
            valid_rows=valid_rows
        )
    
    except HTTPException:
        raise
    except Exception as e:
        errors.append(ValidationError(
            field="file",
            message=f"Unexpected error processing file: {str(e)}"
        ))
        return ValidationResult(
            is_valid=False,
            errors=errors,
            file_name=file_name,
            total_rows=0,
            valid_rows=0
        )


def extract_files_from_zip(zip_bytes: bytes) -> List[Tuple[str, bytes]]:
    """
    Extract files from ZIP archive.
    
    Args:
        zip_bytes: ZIP file content as bytes
    
    Returns:
        List of tuples (filename, file_bytes)
    
    Raises:
        HTTPException: If ZIP cannot be processed
    """
    try:
        files = []
        with zipfile.ZipFile(io.BytesIO(zip_bytes), 'r') as zip_file:
            for file_info in zip_file.infolist():
                if not file_info.is_dir() and file_info.filename.lower().endswith('.csv'):
                    file_bytes = zip_file.read(file_info.filename)
                    files.append((file_info.filename, file_bytes))
        return files
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process ZIP file: {str(e)}")


def validate_multiple_files(files: List[Tuple[str, bytes]], schema: FileSchema) -> List[ValidationResult]:
    """
    Validate multiple files against a schema.
    
    Args:
        files: List of (filename, file_bytes) tuples
        schema: Schema to validate against
    
    Returns:
        List of ValidationResult objects
    """
    results = []
    
    for file_name, file_bytes in files:
        try:
            result = validate_single_file(file_bytes, file_name, schema)
            results.append(result)
        except Exception as e:
            logger.error(f"Error validating {file_name}: {str(e)}")
            results.append(ValidationResult(
                is_valid=False,
                errors=[ValidationError(
                    field="file",
                    message=f"Error processing file: {str(e)}"
                )],
                file_name=file_name,
                total_rows=0,
                valid_rows=0
            ))
    
    return results


def get_schema_by_prefix(prefix: str) -> Optional[FileSchema]:
    """
    Get schema by file prefix.
    
    Args:
        prefix: File prefix (e.g., "DEMO", "DRUG")
    
    Returns:
        FileSchema or None if not found
    """
    return SCHEMA_MAP.get(prefix.upper())


def create_validation_summary(results: List[ValidationResult]) -> Dict[str, Any]:
    """
    Create a summary of validation results.
    
    Args:
        results: List of validation results
    
    Returns:
        Dictionary with validation summary
    """
    total_files = len(results)
    valid_files = sum(1 for r in results if r.is_valid)
    total_rows = sum(r.total_rows for r in results)
    valid_rows = sum(r.valid_rows for r in results)
    
    all_errors = []
    for result in results:
        all_errors.extend(result.errors)
    
    return {
        "total_files": total_files,
        "valid_files": valid_files,
        "invalid_files": total_files - valid_files,
        "total_rows": total_rows,
        "valid_rows": valid_rows,
        "total_errors": len(all_errors),
        "files": [
            {
                "file_name": r.file_name,
                "is_valid": r.is_valid,
                "total_rows": r.total_rows,
                "valid_rows": r.valid_rows,
                "errors": [{"field": e.field, "message": e.message} for e in r.errors]
            }
            for r in results
        ]
    }
