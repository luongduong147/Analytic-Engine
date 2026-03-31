"""Visualization engine for chart generation"""

import matplotlib.pyplot as plt
import plotly.express as px
import pandas as pd
from io import BytesIO
import base64
from typing import Any, Dict, Optional
from ..types import ChartType, VisualizationResult


class VisualizationEngine:
    """Generate charts and visualizations"""

    CHART_METHODS = {
        ChartType.LINE: "_line_chart",
        ChartType.BAR: "_bar_chart",
        ChartType.SCATTER: "_scatter_chart",
        ChartType.PIE: "_pie_chart",
        ChartType.HISTOGRAM: "_histogram",
        ChartType.BOX: "_box_plot",
        ChartType.HEATMAP: "_heatmap",
    }

    def generate(
        self, data: Any, chart_type: ChartType, config: Optional[Dict] = None
    ) -> VisualizationResult:
        """Generate visualization"""
        config = config or {}

        method_name = self.CHART_METHODS.get(chart_type)
        if not method_name:
            raise ValueError(f"Unsupported chart type: {chart_type}")

        method = getattr(self, method_name)
        figure = method(data, config)

        display_data = self._to_display_format(figure, config.get("format", "png"))

        return VisualizationResult(chart_type=chart_type, data=display_data, config=config)

    def _line_chart(self, data: Any, config: Dict) -> Any:
        if config.get("interactive", False):
            return px.line(data, x=config.get("x"), y=config.get("y"))

        fig, ax = plt.subplots()
        if isinstance(data, pd.DataFrame):
            x_col = config.get("x", data.columns[0])
            y_col = config.get("y", data.columns[1])
            ax.plot(data[x_col], data[y_col])
        return fig

    def _bar_chart(self, data: Any, config: Dict) -> Any:
        if config.get("interactive", False):
            return px.bar(data, x=config.get("x"), y=config.get("y"))

        fig, ax = plt.subplots()
        if isinstance(data, pd.DataFrame):
            x_col = config.get("x", data.columns[0])
            y_col = config.get("y", data.columns[1])
            ax.bar(data[x_col], data[y_col])
        return fig

    def _scatter_chart(self, data: Any, config: Dict) -> Any:
        if config.get("interactive", False):
            return px.scatter(data, x=config.get("x"), y=config.get("y"))

        fig, ax = plt.subplots()
        if isinstance(data, pd.DataFrame):
            x_col = config.get("x", data.columns[0])
            y_col = config.get("y", data.columns[1])
            ax.scatter(data[x_col], data[y_col])
        return fig

    def _pie_chart(self, data: Any, config: Dict) -> Any:
        fig, ax = plt.subplots()
        if isinstance(data, dict):
            ax.pie(data.get("values", []), labels=data.get("labels", []))
        return fig

    def _histogram(self, data: Any, config: Dict) -> Any:
        fig, ax = plt.subplots()
        if isinstance(data, pd.DataFrame):
            col = config.get("column", data.columns[0])
            ax.hist(data[col], bins=config.get("bins", 30))
        return fig

    def _box_plot(self, data: Any, config: Dict) -> Any:
        fig, ax = plt.subplots()
        if isinstance(data, pd.DataFrame):
            col = config.get("column", data.columns[0])
            ax.boxplot(data[col].dropna())
        return fig

    def _heatmap(self, data: Any, config: Dict) -> Any:
        import seaborn as sns

        fig, ax = plt.subplots()
        if isinstance(data, pd.DataFrame):
            sns.heatmap(data.corr(), ax=ax, annot=True)
        return fig

    def _to_display_format(self, figure: Any, format: str = "png") -> str:
        """Convert figure to displayable format"""
        if format == "html":
            if hasattr(figure, "to_html"):
                return figure.to_html()

        buf = BytesIO()
        if hasattr(figure, "savefig"):
            figure.savefig(buf, format="png", bbox_inches="tight")
            buf.seek(0)
            return base64.b64encode(buf.read()).decode()

        return ""
