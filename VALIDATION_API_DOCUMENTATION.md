# CSV File Validation API Documentation

This document describes the new file validation system implemented for the FAERS Signal Detection API. The system provides comprehensive validation for multiple CSV file types with specific schemas and data type requirements.

## Overview

The validation system supports:

- **Single file validation**: Upload and validate individual CSV files
- **Multiple file validation**: Upload and validate multiple CSV files at once
- **Folder upload validation**: Validate all CSV files from a folder
- **ZIP file validation**: Extract and validate CSV files from ZIP archives
- **File name validation**: Ensure files start with the correct prefix
- **Column validation**: Verify all required columns are present
- **Data type validation**: Validate column data types (string, integer, timestamp)

## Supported File Types

| File Type | Prefix | Required Columns                                                             | Description        |
| --------- | ------ | ---------------------------------------------------------------------------- | ------------------ |
| DEMO      | DEMO   | primaryid, caseid, caseversion, fda_dt, age, sex, reporter_country, rept_cod | Demographic data   |
| DRUG      | DRUG   | primaryid, caseid, drug_seq, role_cod, drugname, prod_ai                     | Drug information   |
| INDI      | INDI   | primaryid, caseid, indi_drug_seq, indi_pt                                    | Indication data    |
| OUTC      | OUTC   | primaryid, caseid, outc_cod                                                  | Outcome data       |
| REAC      | REAC   | primaryid, caseid, pt                                                        | Reaction data      |
| RPSR      | RPSR   | primaryid, caseid, rpsr_cod                                                  | Report source data |
| THER      | THER   | primaryid, caseid, dsg_drug_seq, start_dt, end_dt, dur, dur_cod              | Therapy data       |

## API Endpoints

### DEMO File Validation

#### Single File Validation

```
POST /demo/validate-single
```

- **Input**: Single CSV file upload
- **Validation**: File name must start with "DEMO"
- **Returns**: Validation result with success/error status

#### Multiple Files Validation

```
POST /demo/validate-multiple
```

- **Input**: Multiple CSV files
- **Validation**: All files must start with "DEMO"
- **Returns**: Summary of validation results for all files

#### ZIP File Validation

```
POST /demo/validate-zip
```

- **Input**: ZIP file containing CSV files
- **Validation**: Extract and validate all CSV files
- **Returns**: Validation results for all extracted files

#### Folder Validation

```
POST /demo/validate-folder
```

- **Input**: Multiple files from folder upload
- **Validation**: Validate all CSV files
- **Returns**: Summary of validation results

#### Schema Information

```
GET /demo/schema
```

- **Returns**: Schema requirements for DEMO files

### DRUG File Validation

#### Single File Validation

```
POST /drug/validate-single
```

- **Input**: Single CSV file upload
- **Validation**: File name must start with "DRUG"
- **Returns**: Validation result with success/error status

#### Multiple Files Validation

```
POST /drug/validate-multiple
```

- **Input**: Multiple CSV files
- **Validation**: All files must start with "DRUG"
- **Returns**: Summary of validation results for all files

#### ZIP File Validation

```
POST /drug/validate-zip
```

- **Input**: ZIP file containing CSV files
- **Validation**: Extract and validate all CSV files
- **Returns**: Validation results for all extracted files

#### Folder Validation

```
POST /drug/validate-folder
```

- **Input**: Multiple files from folder upload
- **Validation**: Validate all CSV files
- **Returns**: Summary of validation results

#### Schema Information

```
GET /drug/schema
```

- **Returns**: Schema requirements for DRUG files

### INDI File Validation

#### Single File Validation

```
POST /indi/validate-single
```

- **Input**: Single CSV file upload
- **Validation**: File name must start with "INDI"
- **Returns**: Validation result with success/error status

#### Multiple Files Validation

```
POST /indi/validate-multiple
```

- **Input**: Multiple CSV files
- **Validation**: All files must start with "INDI"
- **Returns**: Summary of validation results for all files

#### ZIP File Validation

```
POST /indi/validate-zip
```

- **Input**: ZIP file containing CSV files
- **Validation**: Extract and validate all CSV files
- **Returns**: Validation results for all extracted files

#### Folder Validation

```
POST /indi/validate-folder
```

- **Input**: Multiple files from folder upload
- **Validation**: Validate all CSV files
- **Returns**: Summary of validation results

#### Schema Information

```
GET /indi/schema
```

- **Returns**: Schema requirements for INDI files

### OUTC File Validation

#### Single File Validation

```
POST /outc/validate-single
```

- **Input**: Single CSV file upload
- **Validation**: File name must start with "OUTC"
- **Returns**: Validation result with success/error status

#### Multiple Files Validation

```
POST /outc/validate-multiple
```

- **Input**: Multiple CSV files
- **Validation**: All files must start with "OUTC"
- **Returns**: Summary of validation results for all files

#### ZIP File Validation

```
POST /outc/validate-zip
```

- **Input**: ZIP file containing CSV files
- **Validation**: Extract and validate all CSV files
- **Returns**: Validation results for all extracted files

#### Folder Validation

```
POST /outc/validate-folder
```

- **Input**: Multiple files from folder upload
- **Validation**: Validate all CSV files
- **Returns**: Summary of validation results

#### Schema Information

```
GET /outc/schema
```

- **Returns**: Schema requirements for OUTC files

### REAC File Validation

#### Single File Validation

```
POST /reac/validate-single
```

- **Input**: Single CSV file upload
- **Validation**: File name must start with "REAC"
- **Returns**: Validation result with success/error status

#### Multiple Files Validation

```
POST /reac/validate-multiple
```

- **Input**: Multiple CSV files
- **Validation**: All files must start with "REAC"
- **Returns**: Summary of validation results for all files

#### ZIP File Validation

```
POST /reac/validate-zip
```

- **Input**: ZIP file containing CSV files
- **Validation**: Extract and validate all CSV files
- **Returns**: Validation results for all extracted files

#### Folder Validation

```
POST /reac/validate-folder
```

- **Input**: Multiple files from folder upload
- **Validation**: Validate all CSV files
- **Returns**: Summary of validation results

#### Schema Information

```
GET /reac/schema
```

- **Returns**: Schema requirements for REAC files

### RPSR File Validation

#### Single File Validation

```
POST /rpsr/validate-single
```

- **Input**: Single CSV file upload
- **Validation**: File name must start with "RPSR"
- **Returns**: Validation result with success/error status

#### Multiple Files Validation

```
POST /rpsr/validate-multiple
```

- **Input**: Multiple CSV files
- **Validation**: All files must start with "RPSR"
- **Returns**: Summary of validation results for all files

#### ZIP File Validation

```
POST /rpsr/validate-zip
```

- **Input**: ZIP file containing CSV files
- **Validation**: Extract and validate all CSV files
- **Returns**: Validation results for all extracted files

#### Folder Validation

```
POST /rpsr/validate-folder
```

- **Input**: Multiple files from folder upload
- **Validation**: Validate all CSV files
- **Returns**: Summary of validation results

#### Schema Information

```
GET /rpsr/schema
```

- **Returns**: Schema requirements for RPSR files

### THER File Validation

#### Single File Validation

```
POST /ther/validate-single
```

- **Input**: Single CSV file upload
- **Validation**: File name must start with "THER"
- **Returns**: Validation result with success/error status

#### Multiple Files Validation

```
POST /ther/validate-multiple
```

- **Input**: Multiple CSV files
- **Validation**: All files must start with "THER"
- **Returns**: Summary of validation results for all files

#### ZIP File Validation

```
POST /ther/validate-zip
```

- **Input**: ZIP file containing CSV files
- **Validation**: Extract and validate all CSV files
- **Returns**: Validation results for all extracted files

#### Folder Validation

```
POST /ther/validate-folder
```

- **Input**: Multiple files from folder upload
- **Validation**: Validate all CSV files
- **Returns**: Summary of validation results

#### Schema Information

```
GET /ther/schema
```

- **Returns**: Schema requirements for THER files

## Response Formats

### Success Response

```json
{
  "status": "success",
  "message": "File validation passed",
  "file_name": "DEMO_2024.csv",
  "total_rows": 1000,
  "valid_rows": 1000
}
```

### Error Response

```json
{
  "status": "error",
  "message": "File validation failed",
  "file_name": "DEMO_2024.csv",
  "errors": [
    {
      "field": "age",
      "message": "Column 'age' contains 5 non-numeric values"
    }
  ]
}
```

### Multiple Files Summary

```json
{
  "status": "success",
  "message": "All files passed validation",
  "summary": {
    "total_files": 3,
    "valid_files": 3,
    "invalid_files": 0,
    "total_rows": 3000,
    "valid_rows": 3000,
    "total_errors": 0,
    "files": [
      {
        "file_name": "DEMO_2024.csv",
        "is_valid": true,
        "total_rows": 1000,
        "valid_rows": 1000,
        "errors": []
      }
    ]
  }
}
```

## Validation Rules

### File Name Validation

- Files must start with the correct prefix (DEMO, DRUG, INDI, OUTC, REAC, RPSR, THER)
- Case-insensitive matching
- Must be CSV files (.csv extension)

### Column Validation

- All required columns must be present
- Column names are case-insensitive
- Missing columns will cause validation failure

### Data Type Validation

- **Integer**: Must be numeric values
- **String**: Must be text values (null values are allowed for some columns)
- **Timestamp**: Must be valid date format (YYYYMMDD or other recognized formats)

## Error Handling

The system provides detailed error messages for:

- Missing required columns
- Invalid data types
- File name prefix mismatches
- Empty files
- Corrupted CSV files
- ZIP extraction errors

## Usage Examples

### Python Example

```python
import requests

# Single file validation
with open('DEMO_2024.csv', 'rb') as f:
    files = {'file': f}
    response = requests.post('http://localhost:8000/demo/validate-single', files=files)
    print(response.json())

# Multiple files validation
files = [
    ('files', open('DEMO_2024.csv', 'rb')),
    ('files', open('DEMO_2025.csv', 'rb'))
]
response = requests.post('http://localhost:8000/demo/validate-multiple', files=files)
print(response.json())
```

### cURL Example

```bash
# Single file validation
curl -X POST "http://localhost:8000/demo/validate-single" \
  -F "file=@DEMO_2024.csv"

# Get schema information
curl -X GET "http://localhost:8000/demo/schema"
```

## Integration with Existing API

The validation routes are integrated into the existing FastAPI application (`app_v2.py`) without modifying the core functionality. The original endpoints remain unchanged, and the new validation endpoints are available under their respective prefixes.

## File Structure

```
Signal Detector/
├── routes/
│   ├── __init__.py
│   ├── validation_models.py      # Pydantic models and schemas
│   ├── validation_utils.py       # Shared validation utilities
│   ├── demo_routes.py            # DEMO file validation routes
│   ├── drug_routes.py            # DRUG file validation routes
│   ├── indi_routes.py            # INDI file validation routes
│   ├── outc_routes.py            # OUTC file validation routes
│   ├── reac_routes.py            # REAC file validation routes
│   ├── rpsr_routes.py            # RPSR file validation routes
│   └── ther_routes.py            # THER file validation routes
├── app_v2.py                     # Main FastAPI application
└── VALIDATION_API_DOCUMENTATION.md
```

## Testing

Each route includes comprehensive error handling and validation. The system is designed to:

- Reject invalid files immediately
- Provide detailed error messages
- Support batch processing
- Handle various upload scenarios (single, multiple, folder, ZIP)

## Dependencies

The validation system requires:

- FastAPI
- Pandas
- Pydantic
- Python standard library (zipfile, io, os)

All dependencies are already included in the existing project requirements.
