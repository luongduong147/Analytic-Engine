"""Pytest configuration and shared fixtures"""

import pytest
import sys
from pathlib import Path

src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from analytic_engine.sandbox.executor import CodeExecutor
from analytic_engine.semantic.registry import SemanticActionRegistry
from analytic_engine.semantic.actions import create_builtin_actions
from analytic_engine.reasoning.chain import ChainOfThought
from analytic_engine.visualization.engine import VisualizationEngine
from analytic_engine.types import (
    ExecutionConfig,
    AnalysisRequest,
    ReasoningMode,
    ChartType,
)


@pytest.fixture
def execution_config():
    return ExecutionConfig(timeout=30, memory_limit=512)


@pytest.fixture
def code_executor(execution_config):
    return CodeExecutor(config=execution_config)


@pytest.fixture
def semantic_registry():
    return SemanticActionRegistry()


@pytest.fixture
def builtin_actions():
    return create_builtin_actions()


@pytest.fixture
def semantic_registry_with_actions(semantic_registry, builtin_actions):
    for name, handler in builtin_actions.items():
        semantic_registry.register(name, handler)
    return semantic_registry


@pytest.fixture
def cot_reasoner(semantic_registry_with_actions):
    def mock_executor(code, context=None):
        return {"result": "executed"}

    return ChainOfThought(semantic_registry_with_actions, mock_executor)


@pytest.fixture
def visualization_engine():
    return VisualizationEngine()


@pytest.fixture
def sample_dataframe():
    import pandas as pd

    return pd.DataFrame({"x": [1, 2, 3, 4, 5], "y": [2, 4, 6, 8, 10]})


@pytest.fixture
def analysis_request():
    return AnalysisRequest(
        objective="Analyze sales data",
        reasoning_mode=ReasoningMode.CHAIN_OF_THOUGHT,
        max_steps=5,
        context={"data": "sales"},
    )
