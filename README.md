# Analytic Engine Agent

An AI-powered data analysis module that enables LLMs to perform data analysis, forecasting, and visualization through a secure sandbox environment.

## Features

- **Python Sandbox Interpreter** - Secure execution of Python code for data analysis
- **Semantic Layer** - Call data sources via defined semantic actions
- **Reasoning Framework** - Chain of Thought (CoT) and Tree of Thought (ToT) reasoning
- **Visualization Engine** - Generate charts with matplotlib and plotly

## Installation

```bash
pip install -e .
```

## Quick Start

```python
from analytic_engine import AnalyticEngineAgent
from analytic_engine.types import AnalysisRequest, ReasoningMode

agent = AnalyticEngineAgent()

# Execute analysis
request = AnalysisRequest(
    objective="Analyze sales data",
    reasoning_mode=ReasoningMode.CHAIN_OF_THOUGHT
)
result = agent.analyze(request)

# Execute code
code = "import pandas as pd; print(pd.DataFrame({'a': [1,2,3]}))"
result = agent.execute_code(code)
```

## Documentation

- [SPEC.md](SPEC.md) - Detailed architecture specification
- [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md) - Implementation instructions