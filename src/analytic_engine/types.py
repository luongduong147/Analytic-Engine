"""Type definitions for Analytic Engine"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Literal, Type, Optional
from enum import Enum


class ReasoningMode(Enum):
    CHAIN_OF_THOUGHT = "CoT"
    TREE_OF_THOUGHT = "ToT"


class ChartType(Enum):
    LINE = "line"
    BAR = "bar"
    SCATTER = "scatter"
    PIE = "pie"
    HISTOGRAM = "histogram"
    BOX = "box"
    HEATMAP = "heatmap"
    TIME_SERIES = "time_series"


@dataclass
class ExecutionConfig:
    timeout: int = 30
    memory_limit: int = 512
    allowed_packages: List[str] = field(
        default_factory=lambda: [
            "pandas",
            "numpy",
            "scipy",
            "statsmodels",
            "sklearn",
            "matplotlib",
            "plotly",
            "seaborn",
            "json",
            "datetime",
            "math",
            "re",
        ]
    )


@dataclass
class ExecutionResult:
    success: bool
    output: Any = None
    error: Optional[str] = None
    execution_time: float = 0.0
    memory_used: int = 0


@dataclass
class AnalysisRequest:
    objective: str
    reasoning_mode: ReasoningMode = ReasoningMode.CHAIN_OF_THOUGHT
    max_steps: int = 10
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ThoughtStep:
    step_number: int
    thought: str
    action: str
    result: Any
    confidence: float = 1.0
    children: List[ThoughtStep] = field(default_factory=list)


@dataclass
class VisualizationResult:
    chart_type: ChartType
    data: Any
    config: Dict[str, Any]
    display_format: str = "png"


@dataclass
class AnalysisResult:
    answer: str
    data: Any = None
    visualizations: List[VisualizationResult] = field(default_factory=list)
    reasoning_trace: List[ThoughtStep] = field(default_factory=list)
    confidence: float = 0.0
    errors: List[str] = field(default_factory=list)


@dataclass
class SemanticAction:
    name: str
    parameters: Dict[str, Any]
    expected_output: Optional[Type] = None
    handler: Optional[Callable] = None


@dataclass
class ReflectionResult:
    is_valid: bool
    confidence: float
    issues: List[str] = field(default_factory=list)
    suggested_fix: Optional[str] = None


@dataclass
class VerificationResult:
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class ThoughtTree:
    root: ThoughtStep
    best_path: List[ThoughtStep] = field(default_factory=list)
    all_paths: List[List[ThoughtStep]] = field(default_factory=list)
