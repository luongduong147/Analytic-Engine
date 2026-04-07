# AGENTS.md - Analytic Engine Agent

This file provides guidance for AI agents working on this codebase.

## Project Overview

- **Type**: Python library for AI-powered data analysis
- **Location**: `src/analytic_engine/`
- **Python**: 3.10+
- **Test Framework**: pytest

## Build, Lint, and Test Commands

### Install Dependencies
```bash
pip install -e ".[dev]"        # Install with dev dependencies
pip install -e ".[llm]"       # Install with LLM support
```

### Running Tests
```bash
pytest                          # Run all tests
pytest -v                      # Verbose output
pytest tests/                  # Run specific directory
pytest tests/test_sandbox/     # Run specific test module
pytest tests/test_sandbox/test_executor.py::test_function_name  # Run single test
pytest -k "test_name"         # Run tests matching pattern
pytest --cov=analytic_engine   # Run with coverage
pytest --cov=analytic_engine --cov-report=html  # Coverage report
```

### Linting and Formatting
```bash
ruff check src/ tests/                     # Lint with ruff
ruff check src/ --fix                       # Auto-fix issues
black src/ tests/                           # Format code
mypy src/                                   # Type checking
```

### All Checks (CI)
```bash
ruff check src/ tests/ && black --check src/ tests/ && mypy src/ && pytest
```

## Code Style Guidelines

### General
- Line length: 100 characters (enforced by black and ruff)
- Use type hints throughout
- Use dataclasses for data structures (from `dataclasses` import dataclass, field)
- Use `from __future__ import annotations` for forward references

### Imports
- Order: standard library, third-party, local
- Use relative imports within the package: `from .module import ...`
- Group imports by type (types, config, other modules)
- Example:
  ```python
  from typing import Dict, Any, List, Optional, Callable
  from dataclasses import dataclass, field
  
  from .config import Config
  from .types import AnalysisRequest, AnalysisResult
  from .sandbox.executor import CodeExecutor
  ```

### Naming Conventions
- Classes: `PascalCase` (e.g., `AnalyticEngineAgent`)
- Functions/methods: `snake_case` (e.g., `execute_code`)
- Constants: `UPPER_SNAKE_CASE`
- Private methods: `_snake_case` prefix
- Files: `snake_case.py`

### Type Hints
- Use `Dict`, `List`, `Optional` from typing (or use `dict[...]` syntax with Python 3.9+)
- Always specify return types
- Use `Optional[X]` instead of `X | None`
- Example:
  ```python
  def analyze(self, request: AnalysisRequest) -> AnalysisResult:
      ...
  ```

### Dataclasses
- Use `@dataclass` for data containers
- Use `field(default_factory=list)` for mutable defaults
- Example:
  ```python
  @dataclass
  class ExecutionConfig:
      timeout: int = 30
      memory_limit: int = 512
      allowed_packages: List[str] = field(default_factory=list)
  ```

### Error Handling
- Use specific exception types when possible
- Catch exceptions at appropriate boundaries
- Log errors before re-raising
- Return error information in result objects (don't raise for expected conditions)

### Enums
- Use Python `enum.Enum` for enumerated types
- Example:
  ```python
  class ReasoningMode(Enum):
      CHAIN_OF_THOUGHT = "CoT"
      TREE_OF_THOUGHT = "ToT"
  ```

### Class Structure
- Put `__init__` first, then public methods, then private methods
- Use type hints on all methods
- Keep classes focused (single responsibility)

### Testing
- Test files: `tests/test_<module>/test_<component>.py`
- Use pytest fixtures from `conftest.py`
- Follow AAA pattern: Arrange, Act, Assert
- Use descriptive test names: `test_<method>_<expected_behavior>`

### Docstrings
- Use Google-style docstrings for public APIs
- Keep brief (1-2 sentences)
- Example:
  ```python
  def analyze(self, request: AnalysisRequest) -> AnalysisResult:
      """Execute complete analysis request."""
  ```

## Project Structure

```
src/analytic_engine/
├── __init__.py          # Package exports
├── agent.py             # Main agent class
├── config.py            # Configuration
├── types.py             # Type definitions and enums
├── sandbox/             # Code execution sandbox
├── semantic/            # Semantic actions and registry
├── reasoning/           # Reasoning strategies (CoT, ToT)
└── visualization/       # Chart generation
```

## Running the Project

```python
from analytic_engine.agent import AnalyticEngineAgent
from analytic_engine.types import AnalysisRequest, ReasoningMode

agent = AnalyticEngineAgent()
request = AnalysisRequest(objective="Analyze sales data", reasoning_mode=ReasoningMode.CHAIN_OF_THOUGHT)
result = agent.analyze(request)
```

## Key Configuration

- Default timeout: 30 seconds
- Default memory limit: 512MB
- Allowed packages: pandas, numpy, scipy, statsmodels, sklearn, matplotlib, plotly, seaborn
