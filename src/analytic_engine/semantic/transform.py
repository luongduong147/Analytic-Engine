"""Result transformers for semantic layer"""

from typing import Any, Dict, List
import pandas as pd
import json


class ResultTransformer:
    """Transform query results to standardized format"""

    @staticmethod
    def to_dict(data: Any) -> Dict[str, Any]:
        """Convert data to dictionary"""
        if isinstance(data, pd.DataFrame):
            return {
                "columns": list(data.columns),
                "data": data.to_dict("records"),
                "rows": len(data),
            }
        if hasattr(data, "tolist"):
            return {"values": data.tolist()}
        if isinstance(data, (list, tuple)):
            return {"values": list(data)}
        return {"value": data}

    @staticmethod
    def to_json(data: Any) -> str:
        """Convert data to JSON string"""
        return json.dumps(ResultTransformer.to_dict(data))

    @staticmethod
    def to_csv(data: Any) -> str:
        """Convert data to CSV string"""
        if isinstance(data, pd.DataFrame):
            return data.to_csv(index=False)
        return ""

    @staticmethod
    def filter_columns(data: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """Filter to specific columns"""
        return data[[c for c in columns if c in data.columns]]

    @staticmethod
    def apply_filters(data: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
        """Apply filters to dataframe"""
        df = data.copy()
        for col, val in filters.items():
            if col in df.columns:
                df = df[df[col] == val]
        return df
