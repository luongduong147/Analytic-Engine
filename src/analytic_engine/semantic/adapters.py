"""Data source adapter interface"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import pandas as pd


class DataSourceAdapter(ABC):
    """Abstract base class for data source adapters"""

    @abstractmethod
    def query(
        self,
        source: str,
        filters: Optional[Dict] = None,
        columns: Optional[List[str]] = None,
        limit: int = 1000,
    ) -> pd.DataFrame:
        """Query data from source"""
        pass

    @abstractmethod
    def get_schema(self, source: str) -> Dict[str, Any]:
        """Get schema for a source"""
        pass

    @abstractmethod
    def test_connection(self) -> bool:
        """Test if connection is valid"""
        pass


class MockDataAdapter(DataSourceAdapter):
    """Mock data source adapter for testing"""

    def __init__(self, data: Dict[str, pd.DataFrame] = None):
        self._data = data or {}

    def query(
        self,
        source: str,
        filters: Optional[Dict] = None,
        columns: Optional[List[str]] = None,
        limit: int = 1000,
    ) -> pd.DataFrame:
        if source not in self._data:
            return pd.DataFrame()

        df = self._data[source].copy()

        if filters:
            for col, val in filters.items():
                if col in df.columns:
                    df = df[df[col] == val]

        if columns:
            df = df[[c for c in columns if c in df.columns]]

        return df.head(limit)

    def get_schema(self, source: str) -> Dict[str, Any]:
        if source not in self._data:
            return {}

        df = self._data[source]
        return {
            "columns": list(df.columns),
            "dtypes": {c: str(dtype) for c, dtype in df.dtypes.items()},
            "rows": len(df),
        }

    def test_connection(self) -> bool:
        return True


class DataSourceManager:
    """Manages multiple data source adapters"""

    def __init__(self):
        self._adapters: Dict[str, DataSourceAdapter] = {}

    def register(self, name: str, adapter: DataSourceAdapter) -> None:
        """Register a data source adapter"""
        self._adapters[name] = adapter

    def get(self, name: str) -> Optional[DataSourceAdapter]:
        """Get adapter by name"""
        return self._adapters.get(name)

    def list_sources(self) -> List[str]:
        """List all registered sources"""
        return list(self._adapters.keys())
