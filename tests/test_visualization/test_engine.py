"""Tests for visualization engine"""

import pytest
import pandas as pd
from analytic_engine.visualization.engine import VisualizationEngine
from analytic_engine.types import ChartType, VisualizationResult


class TestVisualizationEngine:
    """Test cases for VisualizationEngine"""

    def test_generate_line_chart(self, visualization_engine, sample_dataframe):
        """Test generating a line chart"""
        result = visualization_engine.generate(
            sample_dataframe, ChartType.LINE, {"x": "x", "y": "y"}
        )

        assert result.chart_type == ChartType.LINE
        assert result.data is not None

    def test_generate_bar_chart(self, visualization_engine, sample_dataframe):
        """Test generating a bar chart"""
        result = visualization_engine.generate(
            sample_dataframe, ChartType.BAR, {"x": "x", "y": "y"}
        )

        assert result.chart_type == ChartType.BAR

    def test_generate_scatter_chart(self, visualization_engine, sample_dataframe):
        """Test generating a scatter chart"""
        result = visualization_engine.generate(
            sample_dataframe, ChartType.SCATTER, {"x": "x", "y": "y"}
        )

        assert result.chart_type == ChartType.SCATTER

    def test_generate_pie_chart_with_dict(self, visualization_engine):
        """Test generating a pie chart with dictionary data"""
        data = {"labels": ["A", "B", "C"], "values": [10, 20, 30]}
        result = visualization_engine.generate(data, ChartType.PIE, {})

        assert result.chart_type == ChartType.PIE

    def test_generate_histogram(self, visualization_engine, sample_dataframe):
        """Test generating a histogram"""
        result = visualization_engine.generate(
            sample_dataframe, ChartType.HISTOGRAM, {"column": "x", "bins": 10}
        )

        assert result.chart_type == ChartType.HISTOGRAM

    def test_generate_box_plot(self, visualization_engine, sample_dataframe):
        """Test generating a box plot"""
        result = visualization_engine.generate(sample_dataframe, ChartType.BOX, {"column": "y"})

        assert result.chart_type == ChartType.BOX

    def test_unsupported_chart_type_raises_error(self, visualization_engine):
        """Test unsupported chart type raises ValueError"""
        with pytest.raises(ValueError, match="Unsupported chart type"):
            visualization_engine.generate(pd.DataFrame(), ChartType.TIME_SERIES, {})

    def test_visualization_result_structure(self, visualization_engine, sample_dataframe):
        """Test VisualizationResult has correct structure"""
        result = visualization_engine.generate(
            sample_dataframe, ChartType.LINE, {"x": "x", "y": "y"}
        )

        assert isinstance(result, VisualizationResult)
        assert result.chart_type == ChartType.LINE
        assert isinstance(result.config, dict)

    def test_line_chart_with_defaults(self, visualization_engine, sample_dataframe):
        """Test line chart uses default columns"""
        result = visualization_engine.generate(sample_dataframe, ChartType.LINE, {})

        assert result.chart_type == ChartType.LINE

    def test_bar_chart_with_defaults(self, visualization_engine, sample_dataframe):
        """Test bar chart uses default columns"""
        result = visualization_engine.generate(sample_dataframe, ChartType.BAR, {})

        assert result.chart_type == ChartType.BAR

    def test_to_display_format_png(self, visualization_engine, sample_dataframe):
        """Test converting figure to PNG format"""
        result = visualization_engine.generate(
            sample_dataframe, ChartType.LINE, {"x": "x", "y": "y", "format": "png"}
        )

        assert result.data is not None


class TestChartType:
    """Test cases for ChartType enum"""

    def test_chart_type_values(self):
        """Test ChartType enum values"""
        assert ChartType.LINE.value == "line"
        assert ChartType.BAR.value == "bar"
        assert ChartType.SCATTER.value == "scatter"
        assert ChartType.PIE.value == "pie"
        assert ChartType.HISTOGRAM.value == "histogram"
        assert ChartType.BOX.value == "box"
        assert ChartType.HEATMAP.value == "heatmap"

    def test_all_chart_types_available(self):
        """Test all chart types are available"""
        chart_types = list(ChartType)
        assert len(chart_types) >= 7
        assert ChartType.LINE in chart_types
        assert ChartType.BAR in chart_types
        assert ChartType.SCATTER in chart_types


class TestVisualizationResult:
    """Test cases for VisualizationResult"""

    def test_visualization_result_creation(self):
        """Test creating VisualizationResult"""
        result = VisualizationResult(
            chart_type=ChartType.LINE,
            data="base64data",
            config={"x": "col1", "y": "col2"},
        )

        assert result.chart_type == ChartType.LINE
        assert result.data == "base64data"
        assert result.config == {"x": "col1", "y": "col2"}

    def test_default_display_format(self):
        """Test default display format is png"""
        result = VisualizationResult(
            chart_type=ChartType.BAR,
            data="data",
            config={},
        )

        assert result.display_format == "png"
