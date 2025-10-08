"""
Pydantic models for CSV file validation schemas.
Defines the required columns and data types for each file type.
"""

from typing import List, Optional, Union, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime
import re


class ValidationError(BaseModel):
    """Model for validation error details"""
    field: str
    message: str
    row: Optional[int] = None


class ValidationResult(BaseModel):
    """Model for validation results"""
    is_valid: bool
    errors: List[ValidationError] = []
    file_name: str
    total_rows: int = 0
    valid_rows: int = 0


class FileSchema(BaseModel):
    """Base schema for file validation"""
    file_prefix: str
    required_columns: List[str]
    column_types: dict
    example_row: dict


# File type schemas based on requirements
DEMO_SCHEMA = FileSchema(
    file_prefix="DEMO",
    required_columns=[
        "primaryid", "caseid", "caseversion", "fda_dt", 
        "age", "sex", "reporter_country", "rept_cod"
    ],
    column_types={
        "primaryid": "integer",
        "caseid": "integer", 
        "caseversion": "integer",
        "fda_dt": "timestamp",
        "age": "integer",
        "sex": "string",
        "reporter_country": "string",
        "rept_cod": "string"
    },
    example_row={
        "primaryid": 114582685,
        "caseid": 11458268,
        "caseversion": 5,
        "fda_dt": "20250616",
        "age": None,
        "sex": "F",
        "reporter_country": "US",
        "rept_cod": "EXP"
    }
)

DRUG_SCHEMA = FileSchema(
    file_prefix="DRUG",
    required_columns=[
        "primaryid", "caseid", "drug_seq", "role_cod", 
        "drugname", "prod_ai"
    ],
    column_types={
        "primaryid": "integer",
        "caseid": "integer",
        "drug_seq": "integer", 
        "role_cod": "string",
        "drugname": "string",
        "prod_ai": "string"
    },
    example_row={
        "primaryid": 100236273,
        "caseid": 10023627,
        "drug_seq": 1,
        "role_cod": "PS",
        "drugname": "RISPERDAL",
        "prod_ai": "RISPERIDONE"
    }
)

INDI_SCHEMA = FileSchema(
    file_prefix="INDI",
    required_columns=[
        "primaryid", "caseid", "indi_drug_seq", "indi_pt"
    ],
    column_types={
        "primaryid": "integer",
        "caseid": "integer",
        "indi_drug_seq": "integer",
        "indi_pt": "string"
    },
    example_row={
        "primaryid": 114582685,
        "caseid": 11458268,
        "indi_drug_seq": 1,
        "indi_pt": "Hereditary angioedema"
    }
)

OUTC_SCHEMA = FileSchema(
    file_prefix="OUTC",
    required_columns=[
        "primaryid", "caseid", "outc_cod"
    ],
    column_types={
        "primaryid": "integer",
        "caseid": "integer",
        "outc_cod": "string"
    },
    example_row={
        "primaryid": 114582685,
        "caseid": 11458268,
        "outc_cod": "HO"
    }
)

REAC_SCHEMA = FileSchema(
    file_prefix="REAC",
    required_columns=[
        "primaryid", "caseid", "pt"
    ],
    column_types={
        "primaryid": "integer",
        "caseid": "integer",
        "pt": "string"
    },
    example_row={
        "primaryid": 114582685,
        "caseid": 11458268,
        "pt": "Abdominal pain upper"
    }
)

RPSR_SCHEMA = FileSchema(
    file_prefix="RPSR",
    required_columns=[
        "primaryid", "caseid", "rpsr_cod"
    ],
    column_types={
        "primaryid": "integer",
        "caseid": "integer",
        "rpsr_cod": "string"
    },
    example_row={
        "primaryid": 251359741,
        "caseid": 25135974,
        "rpsr_cod": "CSM"
    }
)

THER_SCHEMA = FileSchema(
    file_prefix="THER",
    required_columns=[
        "primaryid", "caseid", "dsg_drug_seq", "start_dt", 
        "end_dt", "dur", "dur_cod"
    ],
    column_types={
        "primaryid": "integer",
        "caseid": "integer",
        "dsg_drug_seq": "integer",
        "start_dt": "timestamp",
        "end_dt": "timestamp", 
        "dur": "integer",
        "dur_cod": "string"
    },
    example_row={
        "primaryid": 1223393219,
        "caseid": 12233932,
        "dsg_drug_seq": 2,
        "start_dt": "20141015",
        "end_dt": "20150506",
        "dur": 204,
        "dur_cod": "DAY"
    }
)

# Schema mapping for easy access
SCHEMA_MAP = {
    "DEMO": DEMO_SCHEMA,
    "DRUG": DRUG_SCHEMA,
    "INDI": INDI_SCHEMA,
    "OUTC": OUTC_SCHEMA,
    "REAC": REAC_SCHEMA,
    "RPSR": RPSR_SCHEMA,
    "THER": THER_SCHEMA
}
