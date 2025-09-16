"""
JSON Serialization utilities for handling numpy and pandas types
"""

import json
import numpy as np
import pandas as pd
from datetime import datetime, date
from decimal import Decimal
from enum import Enum


class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle numpy types and other non-serializable objects"""
    
    def default(self, obj):
        if isinstance(obj, (np.integer, np.int64, np.int32, np.int16, np.int8)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64, np.float32, np.float16)):
            if np.isnan(obj):
                return None
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, (datetime, date)):
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, Enum):
            return obj.value
        elif pd.isna(obj):
            return None
        # Handle pandas Series and other types that might have int64
        elif hasattr(obj, 'dtype') and 'int' in str(obj.dtype):
            return int(obj)
        elif hasattr(obj, 'dtype') and 'float' in str(obj.dtype):
            return float(obj)
        return super().default(obj)


def safe_json_serialize(data):
    """Safely serialize data to JSON with custom encoder"""
    return json.dumps(data, cls=CustomJSONEncoder, ensure_ascii=False)


def convert_numpy_types(obj):
    """Recursively convert numpy types to Python native types"""
    if isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    elif isinstance(obj, (np.integer, np.int64, np.int32, np.int16, np.int8)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32, np.float16)):
        if np.isnan(obj):
            return None
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif pd.isna(obj) or (isinstance(obj, float) and np.isnan(obj)):
        return None
    elif hasattr(obj, 'item'):  # numpy scalar
        return obj.item()
    elif hasattr(obj, 'dtype') and 'int' in str(obj.dtype):
        return int(obj)
    elif hasattr(obj, 'dtype') and 'float' in str(obj.dtype):
        return float(obj)
    return obj


def prepare_for_jsonb(data):
    """Prepare data for storage in PostgreSQL JSONB column"""
    if data is None:
        return None
    
    # Convert numpy types to native Python types
    converted = convert_numpy_types(data)
    
    # Ensure it's JSON serializable
    try:
        json.dumps(converted, cls=CustomJSONEncoder)
        return converted
    except (TypeError, ValueError) as e:
        # If still not serializable, convert to string representation
        return str(converted)
