"""Built-in semantic actions"""

import pandas as pd
from typing import Dict, Any, List, Callable, Optional


def create_builtin_actions(data_accessor: Optional[Callable] = None) -> Dict[str, Callable]:
    """Create built-in semantic actions"""

    def query_data(
        source: str,
        filters: Optional[Dict] = None,
        columns: Optional[List] = None,
        limit: int = 1000,
    ) -> pd.DataFrame:
        """Query data from a data source"""
        if data_accessor:
            return data_accessor.query(source, filters or {}, columns, limit)
        return pd.DataFrame()

    def fetch_metrics(metric_names: List[str], timeframe: str = "7d") -> Dict[str, Any]:
        """Fetch specific metrics"""
        return {metric: None for metric in metric_names}

    def get_historical_data(entity: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Get historical data for an entity"""
        return pd.DataFrame()

    def get_aggregated(
        source: str, agg_func: str = "sum", group_by: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """Get aggregated data"""
        return pd.DataFrame()

    return {
        "query_data": query_data,
        "fetch_metrics": fetch_metrics,
        "get_historical_data": get_historical_data,
        "get_aggregated": get_aggregated,
    }
