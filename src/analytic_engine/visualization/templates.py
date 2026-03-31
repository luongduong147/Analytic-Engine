"""Chart templates for visualization engine"""

from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass


@dataclass
class ChartTemplate:
    name: str
    chart_type: str
    required_config: list
    render_func: Optional[Callable] = None


class TemplateLibrary:
    """Library of pre-built chart templates"""

    TEMPLATES = {
        "trends": {
            "chart_type": "line",
            "description": "Time series trends",
            "config": {"x": "date", "y": "value", "interactive": True},
        },
        "comparison": {
            "chart_type": "bar",
            "description": "Compare values across categories",
            "config": {"x": "category", "y": "value", "orientation": "vertical"},
        },
        "distribution": {
            "chart_type": "histogram",
            "description": "Data distribution visualization",
            "config": {"column": "value", "bins": 30},
        },
        "correlation": {
            "chart_type": "heatmap",
            "description": "Correlation matrix",
            "config": {"annot": True},
        },
        "proportion": {
            "chart_type": "pie",
            "description": "Parts of a whole",
            "config": {"labels": "category", "values": "value"},
        },
        "outliers": {
            "chart_type": "box",
            "description": "Box plot for outlier detection",
            "config": {"column": "value"},
        },
        "scatter": {
            "chart_type": "scatter",
            "description": "XY scatter plot",
            "config": {"x": "x_value", "y": "y_value"},
        },
    }

    @classmethod
    def get_template(cls, name: str) -> Optional[Dict[str, Any]]:
        """Get template by name"""
        return cls.TEMPLATES.get(name)

    @classmethod
    def list_templates(cls) -> list:
        """List all available templates"""
        return list(cls.TEMPLATES.keys())

    @classmethod
    def apply_template(cls, name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply template config to user config"""
        template = cls.get_template(name)
        if not template:
            return config

        merged = template["config"].copy()
        merged.update(config)
        return merged
