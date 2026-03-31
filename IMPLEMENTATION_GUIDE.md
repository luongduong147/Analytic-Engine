# Analytic Engine Agent - Implementation Guide

## Getting Started

This guide walks through implementing each component in priority order.

---

## Phase 1: Foundation

### 1.1 Type Definitions (`src/analytic_engine/types.py`)

```python
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Literal, Type, Optional
from enum import Enum

# Enums
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

# Data Classes
@dataclass
class ExecutionConfig:
    timeout: int = 30
    memory_limit: int = 512
    allowed_packages: List[str] = field(default_factory=lambda: [
        "pandas", "numpy", "scipy", "statsmodels", "sklearn",
        "matplotlib", "plotly", "seaborn", "json", "datetime", "math", "re"
    ])

@dataclass
class ExecutionResult:
    success: bool
    output: Any
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
    display_format: str = "png"  # or "html" for plotly

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
```

---

### 1.2 Config Management (`src/analytic_engine/config.py`)

```python
from typing import Dict, Any
from .types import ExecutionConfig

class Config:
    def __init__(self, custom: Dict[str, Any] = None):
        self.execution = ExecutionConfig()
        self._custom = custom or {}
    
    def get(self, key: str, default: Any = None) -> Any:
        return self._custom.get(key, default)
    
    def set_execution_limit(self, timeout: int = None, memory: int = None):
        if timeout:
            self.execution.timeout = timeout
        if memory:
            self.execution.memory_limit = memory
    
    @property
    def default_packages(self) -> list:
        return self.execution.allowed_packages
```

---

### 1.3 Sandbox Executor (`src/analytic_engine/sandbox/executor.py`)

```python
import subprocess
import tempfile
import time
import json
from pathlib import Path
from typing import Optional
from ..types import ExecutionConfig, ExecutionResult

class CodeExecutor:
    """Secure Python code execution in isolated environment"""
    
    DANGEROUS_IMPORTS = [
        "os", "sys", "subprocess", "socket", "requests",
        "urllib", "http", "ftplib", "smtplib", "pty",
        "importlib", "builtins", "exec", "eval", "compile"
    ]
    
    def __init__(self, config: ExecutionConfig = None):
        self.config = config or ExecutionConfig()
    
    def validate_code(self, code: str) -> tuple[bool, Optional[str]]:
        """Check for dangerous operations before execution"""
        lines = code.split('\n')
        for line in lines:
            # Check for dangerous imports
            for dangerous in self.DANGEROUS_IMPORTS:
                if f"import {dangerous}" in line or f"from {dangerous} " in line:
                    return False, f"Import '{dangerous}' is not allowed"
            
            # Check for dangerous functions
            if any(x in line for x in ["eval(", "exec(", "compile("]):
                return False, "Dynamic code execution is not allowed"
        
        return True, None
    
    def execute(self, code: str, context: dict = None) -> ExecutionResult:
        """Execute Python code in sandbox"""
        start_time = time.time()
        
        # Validate code first
        is_valid, error = self.validate_code(code)
        if not is_valid:
            return ExecutionResult(
                success=False,
                output=None,
                error=error,
                execution_time=time.time() - start_time
            )
        
        # Build execution context
        context_code = ""
        if context:
            context_code = "\n".join([f"{k} = {repr(v)}" for k, v in context.items()])
            code = f"{context_code}\n{code}"
        
        try:
            result = self._execute_isolated(code)
            return ExecutionResult(
                success=True,
                output=result,
                execution_time=time.time() - start_time
            )
        except Exception as e:
            return ExecutionResult(
                success=False,
                output=None,
                error=str(e),
                execution_time=time.time() - start_time
            )
    
    def _execute_isolated(self, code: str) -> Any:
        """Execute in subprocess with limits"""
        # Create temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_path = f.name
        
        try:
            # Execute with timeout
            result = subprocess.run(
                ['python', temp_path],
                capture_output=True,
                text=True,
                timeout=self.config.timeout,
                cwd=tempfile.gettempdir()
            )
            
            if result.returncode != 0:
                raise Exception(result.stderr)
            
            # Parse output
            if result.stdout.strip():
                # Try to parse as JSON first
                try:
                    return json.loads(result.stdout)
                except json.JSONDecodeError:
                    return result.stdout.strip()
            
            return None
            
        finally:
            Path(temp_path).unlink(missing_ok=True)
```

---

## Phase 2: Core Logic

### 2.1 Semantic Layer - Action Registry (`src/analytic_engine/semantic/registry.py`)

```python
from typing import Dict, Callable, Any
from ..types import SemanticAction

class SemanticActionRegistry:
    """Registry for semantic actions that agents can call"""
    
    def __init__(self):
        self._actions: Dict[str, Callable] = {}
    
    def register(self, name: str, handler: Callable) -> None:
        """Register a semantic action"""
        self._actions[name] = handler
    
    def execute(self, action_name: str, params: dict) -> Any:
        """Execute a registered action"""
        if action_name not in self._actions:
            raise ValueError(f"Unknown action: {action_name}")
        
        return self._actions[action_name](**params)
    
    def list_actions(self) -> list:
        """List all registered actions"""
        return list(self._actions.keys())
    
    def get_action(self, name: str) -> Callable:
        """Get action handler"""
        return self._actions.get(name)
```

### 2.2 Built-in Semantic Actions (`src/analytic_engine/semantic/actions.py`)

```python
import pandas as pd
from typing import Dict, Any, List
from .registry import SemanticActionRegistry

def create_builtin_actions(data_accessor: Callable = None) -> Dict[str, Callable]:
    """Create built-in semantic actions"""
    
    def query_data(source: str, filters: Dict = None, 
                   columns: List = None, limit: int = 1000) -> pd.DataFrame:
        """Query data from a data source"""
        # Implementation depends on data_accessor
        if data_accessor:
            return data_accessor.query(source, filters, columns, limit)
        return pd.DataFrame()  # Placeholder
    
    def fetch_metrics(metric_names: List[str], 
                      timeframe: str = "7d") -> Dict[str, Any]:
        """Fetch specific metrics"""
        # Placeholder implementation
        return {metric: None for metric in metric_names}
    
    def get_historical_data(entity: str, start_date: str, 
                           end_date: str) -> pd.DataFrame:
        """Get historical data for an entity"""
        # Placeholder implementation  
        return pd.DataFrame()
    
    def get_aggregated(source: str, agg_func: str = "sum",
                      group_by: List[str] = None) -> pd.DataFrame:
        """Get aggregated data"""
        # Placeholder implementation
        return pd.DataFrame()
    
    return {
        "query_data": query_data,
        "fetch_metrics": fetch_metrics,
        "get_historical_data": get_historical_data,
        "get_aggregated": get_aggregated
    }
```

---

### 2.3 Reasoning Framework - Chain of Thought (`src/analytic_engine/reasoning/chain.py`)

```python
from typing import List, Optional
from ..types import (
    AnalysisRequest, ThoughtStep, ReasoningMode, 
    ExecutionResult, SemanticActionRegistry
)

class ChainOfThought:
    """Chain of Thought reasoning implementation"""
    
    def __init__(self, semantic_registry: SemanticActionRegistry, 
                 executor: Callable):
        self.semantic = semantic_registry
        self.executor = executor
        self.max_steps = 10
    
    def reason(self, request: AnalysisRequest) -> List[ThoughtStep]:
        """Execute chain of thought reasoning"""
        steps = []
        current_context = request.context.copy()
        
        for step_num in range(1, request.max_steps + 1):
            # Analyze current state and determine next step
            thought = self._analyze_step(step_num, current_context)
            
            # Execute step
            action, params = self._determine_action(thought)
            result = self._execute_action(action, params)
            
            step = ThoughtStep(
                step_number=step_num,
                thought=thought,
                action=action,
                result=result
            )
            steps.append(step)
            
            # Update context
            current_context[f"step_{step_num}"] = result
            
            # Check if complete
            if self._is_complete(step, steps):
                break
        
        return steps
    
    def _analyze_step(self, step_num: int, context: dict) -> str:
        """Analyze current state to determine next thought"""
        # Placeholder: In real implementation, use LLM to analyze
        return f"Step {step_num}: Analyze context and determine next action"
    
    def _determine_action(self, thought: str) -> tuple[str, dict]:
        """Determine action based on thought"""
        # Placeholder: Parse thought to determine semantic action
        return ("query_data", {"source": "default", "limit": 100})
    
    def _execute_action(self, action: str, params: dict) -> Any:
        """Execute the determined action"""
        if action in self.semantic.list_actions():
            return self.semantic.execute(action, params)
        return None
    
    def _is_complete(self, step: ThoughtStep, 
                     all_steps: List[ThoughtStep]) -> bool:
        """Check if reasoning is complete"""
        # Placeholder: Check if objective seems achieved
        return step_num >= len(all_steps)
```

---

### 2.4 Visualization Engine (`src/analytic_engine/visualization/engine.py`)

```python
import matplotlib.pyplot as plt
import plotly.express as px
import pandas as pd
from io import BytesIO
import base64
from typing import Any, Dict
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
    
    def generate(self, data: Any, chart_type: ChartType, 
                 config: Dict = None) -> VisualizationResult:
        """Generate visualization"""
        config = config or {}
        
        method_name = self.CHART_METHODS.get(chart_type)
        if not method_name:
            raise ValueError(f"Unsupported chart type: {chart_type}")
        
        method = getattr(self, method_name)
        figure = method(data, config)
        
        # Convert to display format
        display_data = self._to_display_format(figure, config.get("format", "png"))
        
        return VisualizationResult(
            chart_type=chart_type,
            data=display_data,
            config=config
        )
    
    def _line_chart(self, data: pd.DataFrame, config: Dict) -> Any:
        """Create line chart"""
        if config.get("interactive", False):
            return px.line(data, x=config.get("x"), y=config.get("y"))
        
        fig, ax = plt.subplots()
        ax.plot(data[config.get("x", data.columns[0])], 
                data[config.get("y", data.columns[1])])
        return fig
    
    def _bar_chart(self, data: pd.DataFrame, config: Dict) -> Any:
        """Create bar chart"""
        if config.get("interactive", False):
            return px.bar(data, x=config.get("x"), y=config.get("y"))
        
        fig, ax = plt.subplots()
        ax.bar(data[config.get("x", data.columns[0])], 
               data[config.get("y", data.columns[1])])
        return fig
    
    def _scatter_chart(self, data: pd.DataFrame, config: Dict) -> Any:
        """Create scatter chart"""
        if config.get("interactive", False):
            return px.scatter(data, x=config.get("x"), y=config.get("y"))
        
        fig, ax = plt.subplots()
        ax.scatter(data[config.get("x", data.columns[0])], 
                    data[config.get("y", data.columns[1])])
        return fig
    
    def _pie_chart(self, data: pd.DataFrame, config: Dict) -> Any:
        """Create pie chart"""
        fig, ax = plt.subplots()
        ax.pie(data[config.get("values", data.columns[1])], 
               labels=data[config.get("labels", data.columns[0])])
        return fig
    
    def _histogram(self, data: pd.DataFrame, config: Dict) -> Any:
        """Create histogram"""
        fig, ax = plt.subplots()
        col = config.get("column", data.columns[0])
        ax.hist(data[col], bins=config.get("bins", 30))
        return fig
    
    def _box_plot(self, data: pd.DataFrame, config: Dict) -> Any:
        """Create box plot"""
        fig, ax = plt.subplots()
        col = config.get("column", data.columns[0])
        ax.boxplot(data[col].dropna())
        return fig
    
    def _heatmap(self, data: pd.DataFrame, config: Dict) -> Any:
        """Create heatmap"""
        import seaborn as sns
        fig, ax = plt.subplots()
        sns.heatmap(data.corr(), ax=ax, annot=True)
        return fig
    
    def _to_display_format(self, figure: Any, format: str = "png") -> str:
        """Convert figure to displayable format"""
        if format == "html":
            if hasattr(figure, "to_html"):
                return figure.to_html()
        
        # PNG via matplotlib
        buf = BytesIO()
        if hasattr(figure, "savefig"):
            figure.savefig(buf, format="png", bbox_inches="tight")
            buf.seek(0)
            return base64.b64encode(buf.read()).decode()
        
        return ""
```

---

## Phase 3: Main Agent

### 3.1 Main Agent (`src/analytic_engine/agent.py`)

```python
from typing import Dict, Any, Optional
from .config import Config
from .types import (
    AnalysisRequest, AnalysisResult, ExecutionConfig,
    ReasoningMode, ChartType, ExecutionResult as ExecResult
)
from .sandbox.executor import CodeExecutor
from .semantic.registry import SemanticActionRegistry
from .semantic.actions import create_builtin_actions
from .reasoning.chain import ChainOfThought
from .visualization.engine import VisualizationEngine

class AnalyticEngineAgent:
    """Main entry point for the analytic engine"""
    
    def __init__(self, config: Dict = None):
        self.config = Config(config)
        
        # Initialize components
        self.sandbox = CodeExecutor(self.config.execution)
        self.semantic = SemanticActionRegistry()
        self.viz = VisualizationEngine()
        
        # Register built-in semantic actions
        self._register_actions()
        
        # Initialize reasoning
        self.reasoning = ChainOfThought(self.semantic, self.sandbox.execute)
    
    def _register_actions(self):
        """Register built-in semantic actions"""
        actions = create_builtin_actions()
        for name, handler in actions.items():
            self.semantic.register(name, handler)
    
    def analyze(self, request: AnalysisRequest) -> AnalysisResult:
        """Execute complete analysis request"""
        try:
            # Step 1: Reasoning
            if request.reasoning_mode == ReasoningMode.CHAIN_OF_THOUGHT:
                reasoning_trace = self.reasoning.reason(request)
            else:
                reasoning_trace = self.reasoning.reason(request)  # ToT placeholder
            
            # Step 2: Extract answer from reasoning
            answer = self._extract_answer(reasoning_trace)
            
            return AnalysisResult(
                answer=answer,
                data=reasoning_trace[-1].result if reasoning_trace else None,
                reasoning_trace=reasoning_trace,
                confidence=1.0
            )
            
        except Exception as e:
            return AnalysisResult(
                answer="",
                errors=[str(e)],
                confidence=0.0
            )
    
    def execute_code(self, code: str, context: Dict = None) -> ExecResult:
        """Execute Python code in sandbox"""
        return self.sandbox.execute(code, context)
    
    def fetch_data(self, action: str, params: Dict) -> Any:
        """Fetch data via semantic actions"""
        return self.semantic.execute(action, params)
    
    def visualize(self, data: Any, chart_type: str, 
                 config: Dict = None) -> Any:
        """Generate visualization"""
        return self.viz.generate(data, ChartType(chart_type), config)
    
    def _extract_answer(self, reasoning_trace) -> str:
        """Extract final answer from reasoning trace"""
        if not reasoning_trace:
            return "No reasoning steps completed"
        
        last_step = reasoning_trace[-1]
        return f"Analysis completed with {len(reasoning_trace)} steps"
```

---

## Phase 4: Usage Example

### 4.1 Basic Usage (`examples/basic_analysis.py`)

```python
from analytic_engine import AnalyticEngineAgent
from analytic_engine.types import AnalysisRequest, ReasoningMode

# Initialize agent
agent = AnalyticEngineAgent()

# Execute analysis
request = AnalysisRequest(
    objective="Analyze sales data and find trends",
    reasoning_mode=ReasoningMode.CHAIN_OF_THOUGHT,
    max_steps=5
)

result = agent.analyze(request)
print(result.answer)
print(f"Confidence: {result.confidence}")

# Direct code execution
code = """
import pandas as pd
import numpy as np

# Create sample data
data = pd.DataFrame({
    'date': pd.date_range('2024-01-01', periods=30),
    'sales': np.random.randint(100, 500, 30)
})

# Calculate summary
summary = data['sales'].describe()
print(summary.to_json())
"""

exec_result = agent.execute_code(code)
if exec_result.success:
    print(exec_result.output)

# Generate visualization
chart_result = agent.visualize(
    data={"values": [10, 20, 30], "labels": ["A", "B", "C"]},
    chart_type="pie",
    config={"format": "html"}
)
print(chart_result.chart_type)
```

---

## Next Steps

1. Run `pip install -e .` to install the package
2. Run tests in `tests/` to verify components
3. Extend semantic layer with real data sources
4. Implement Tree of Thought reasoning
5. Add more visualization templates