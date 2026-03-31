"""Analytic Engine Agent - AI-powered data analysis module"""

from .agent import AnalyticEngineAgent
from .types import (
    AnalysisRequest,
    AnalysisResult,
    ExecutionConfig,
    ExecutionResult,
    ReasoningMode,
    ChartType,
    ThoughtStep,
    VisualizationResult,
)

__version__ = "0.1.0"
__all__ = [
    "AnalyticEngineAgent",
    "AnalysisRequest",
    "AnalysisResult",
    "ExecutionConfig",
    "ExecutionResult",
    "ReasoningMode",
    "ChartType",
    "ThoughtStep",
    "VisualizationResult",
]
