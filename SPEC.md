# Analytic Engine Agent - Architecture Specification

## 1. Project Overview

**Project Name:** Analytic Engine Agent  
**Type:** AI-powered data analysis module (agentic system)  
**Core Functionality:** Enables LLMs to perform data analysis, forecasting, and visualization through a secure sandbox environment with semantic data access and multi-step reasoning capabilities.  
**Target Users:** LLMs requiring data analysis capabilities, data science teams, analytics applications.

---

## 2. System Architecture

### 2.1 Component Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ANALYTIC ENGINE AGENT                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐     │
│  │   USER/LLM       │───▶│  Reasoning       │───▶│   Semantic       │     │
│  │   Interface      │    │   Framework      │    │   Layer          │     │
│  └──────────────────┘    └──────────────────┘    └──────────────────┘     │
│                                  │                         │              │
│                                  ▼                         ▼              │
│                          ┌──────────────────┐    ┌──────────────────┐     │
│                          │  Visualization  │◀───│  Python Sandbox  │     │
│                          │    Engine        │    │   Interpreter   │     │
│                          └──────────────────┘    └──────────────────┘     │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Component Details

#### A. Python Sandbox Interpreter
**Purpose:** Secure execution environment for data analysis code

**Components:**
- `SandboxManager`: Manages isolated execution environments
- `CodeExecutor`: Executes Python code with resource limits
- `DependencyManager`: Loads and manages allowed packages
- `ExecutionResult`: Standardized output format

**Security Features:**
- Process isolation (subprocess/namespace)
- Memory limits (configurable, default 512MB)
- CPU time limits (configurable, default 30s)
- No network access in sandbox
- No file system write access (except temp)
- Whitelist-based package import

**Supported Libraries:**
- Data: pandas, numpy, scipy, statsmodels
- ML: scikit-learn, prophet
- Visualization: matplotlib, plotly, seaborn
- Utilities: json, datetime, math, re

#### B. Semantic Layer
**Purpose:** Enable data source integration through defined actions

**Components:**
- `SemanticActionRegistry`: Maps action names to handlers
- `DataSourceAdapter`: Interface for external data sources
- `QueryBuilder`: Constructs data queries from semantic intent
- `ResultTransformer`: Converts data to standardized format

**Defined Semantic Actions:**
| Action | Parameters | Returns |
|--------|-----------|---------|
| `query_data` | source, filters, columns, limit | DataFrame |
| `fetch_metrics` | metric_names, timeframe | Dict |
| `get_historical_data` | entity, start_date, end_date | DataFrame |
| `get_aggregated` | source, agg_func, group_by | DataFrame |

#### C. Reasoning Framework
**Purpose:** Multi-step reasoning with self-verification and skill retrieval

**Components:**
- `ReasoningOrchestrator`: Manages reasoning flow
- `ThoughtTree`: Stores reasoning steps and branches
- `ChainBuilder`: Builds sequential reasoning chains
- `SelfReflector`: Evaluates reasoning quality
- `VerificationEngine`: Validates intermediate results
- `SkillManager`: Manages skill retrieval for context injection

**Skill System (Agent Tool):**
- `SkillManager`: Loads and manages skills from markdown files
- `Skill`: Represents a skill with name, category, content, and tags
- Similar to `/skill` command in OpenCode/Claude Code

**Skill Retrieval API:**
```python
agent.get_skill(name: str) -> Optional[Skill]
agent.get_skill_content(name: str) -> Optional[str]
agent.list_skills() -> List[str]
agent.search_skills(query: str) -> List[Skill]
agent.get_skill_for_task(task: str) -> Optional[Skill]
```

**Skill File Structure:**
```
skills/
├── business_analysis/
│   └── skill.md          # Markdown skill file
├── data_processing/
│   └── skill.md
└── ...
```

**Reasoning Modes:**
1. **Chain of Thought (CoT):** Sequential step-by-step reasoning
2. **Tree of Thought (ToT):** Parallel exploration of multiple paths

**Note:** CoT logic can be injected into prompt for Business Analyst agent to handle (future enhancement).

**Self-Reflection Features:**
- Confidence scoring per step
- Error detection and recovery
- Alternative path exploration
- Result verification against constraints

**Self-Reflection Features:**
- Confidence scoring per step
- Error detection and recovery
- Alternative path exploration
- Result verification against constraints

#### D. Visualization Engine
**Purpose:** Generate user-friendly chart outputs

**Components:**
- `ChartGenerator`: Creates visualizations from data
- `OutputFormatter`: Converts to displayable formats
- `TemplateLibrary`: Pre-built chart templates
- `InteractiveRenderer`: For plotly interactive charts

**Supported Chart Types:**
- Line, Bar, Scatter, Pie charts
- Histograms, Box plots
- Time series plots
- Heatmaps, Correlation matrices

---

## 3. Data Flow

### 3.1 Primary Flow

```
1. REQUEST
   User/LLM sends analysis request
          │
          ▼
2. REASONING
   Reasoning Framework analyzes request
   - Decomposes into steps
   - Identifies required data
   - Plans execution strategy
          │
          ▼
3. DATA FETCH (Semantic Layer)
   Call semantic actions to fetch data
   - Resolve data source
   - Apply filters
   - Return structured data
          │
          ▼
4. EXECUTE (Sandbox)
   Execute analysis code
   - Write code to sandbox
   - Run with resource limits
   - Capture output/errors
          │
          ▼
5. VERIFY (Reasoning)
   Self-reflect on results
   - Check correctness
   - Validate constraints
   - Retry if needed
          │
          ▼
6. VISUALIZE
   Generate charts
   - Create matplotlib/plotly figures
   - Convert to displayable format
          │
          ▼
7. RESPONSE
   Return results + visualizations
```

### 3.2 Error Handling Flow

```
Error detected ──▶ Log error details ──▶ Check retry limit
       │                                        │
       ▼                                        ▼
  Return error    ┌──────────────────────────────┘
  to user         │ (if retry available)
                  ▼
            Retry with modified strategy
                  │
                  ▼
         Max retries ──▶ Return failure with details
```

---

## 4. Interface Definitions

### 4.1 Public API

```python
class AnalyticEngineAgent:
    """Main entry point for the analytic engine"""
    
    def analyze(self, request: AnalysisRequest) -> AnalysisResult:
        """Execute complete analysis request"""
        
    def execute_code(self, code: str, context: dict) -> ExecutionResult:
        """Execute Python code in sandbox"""
        
    def fetch_data(self, action: str, params: dict) -> Any:
        """Fetch data via semantic actions"""
        
    def visualize(self, data: Any, chart_type: str, config: dict) -> VisualizationResult:
        """Generate visualization"""
```

### 4.2 Data Structures

```python
# Request/Response
@dataclass
class AnalysisRequest:
    objective: str
    reasoning_mode: Literal["CoT", "ToT"]
    max_steps: int = 10
    context: dict = field(default_factory=dict)

@dataclass
class AnalysisResult:
    answer: str
    data: Any
    visualizations: List[VisualizationResult]
    reasoning_trace: List[ThoughtStep]
    confidence: float
    errors: List[str]

# Semantic Layer
@dataclass
class SemanticAction:
    name: str
    parameters: Dict[str, Any]
    expected_output: Type
    
# Sandbox
@dataclass
class ExecutionConfig:
    timeout: int = 30          # seconds
    memory_limit: int = 512    # MB
    allowed_packages: List[str] = field(default_factory=lambda: DEFAULT_PACKAGES)
    
@dataclass
class ExecutionResult:
    success: bool
    output: Any
    error: str = None
    execution_time: float
    memory_used: int
```

### 4.3 Component Interfaces

```python
# Sandbox Interface
class ISandbox(Protocol):
    def execute(self, code: str, config: ExecutionConfig) -> ExecutionResult: ...
    def validate_code(self, code: str) -> bool: ...
    
# Semantic Layer Interface  
class ISemanticLayer(Protocol):
    def register_action(self, name: str, handler: Callable) -> None: ...
    def execute_action(self, action: str, params: dict) -> Any: ...
    def list_actions(self) -> List[str]: ...

# Reasoning Interface
class IReasoningFramework(Protocol):
    def reason(self, request: AnalysisRequest) -> ThoughtTree: ...
    def reflect(self, result: Any) -> ReflectionResult: ...
    def verify(self, result: Any, constraints: dict) -> VerificationResult: ...

# Visualization Interface
class IVisualizationEngine(Protocol):
    def generate(self, data: Any, chart_type: str, config: dict) -> VisualizationResult: ...
    def to_display_format(self, viz: Any) -> DisplayFormat: ...
```

---

## 5. File Structure

```
analytic-engine-agent/
├── SPEC.md
├── README.md
├── requirements.txt
├── pyproject.toml
│
├── src/
│   └── analytic_engine/
│       ├── __init__.py
│       ├── agent.py                 # Main agent class
│       ├── config.py                # Configuration management
│       ├── types.py                 # Type definitions
│       │
│       ├── sandbox/                 # Component 1: Sandbox
│       │   ├── __init__.py
│       │   ├── manager.py           # Sandbox manager
│       │   ├── executor.py          # Code executor
│       │   ├── security.py          # Security validation
│       │   └── packages.py          # Allowed packages
│       │
│       ├── semantic/                # Component 2: Semantic Layer
│       │   ├── __init__.py
│       │   ├── registry.py          # Action registry
│       │   ├── actions.py           # Built-in actions
│       │   ├── adapters.py         # Data source adapters
│       │   └── transform.py         # Result transformers
│       │
│       ├── reasoning/               # Component 3: Reasoning
│       │   ├── __init__.py
│       │   ├── orchestrator.py      # Main orchestrator
│       │   ├── thought_tree.py      # ToT implementation
│       │   ├── chain.py             # CoT implementation
│       │   ├── reflector.py         # Self-reflection
│       │   └── verifier.py          # Result verification
│       │
│       └── visualization/           # Component 4: Visualization
│           ├── __init__.py
│           ├── engine.py            # Chart generation
│           ├── templates.py         # Chart templates
│           └── formatters.py        # Output formatters
│
├── tests/
│   ├── __init__.py
│   ├── test_sandbox/
│   ├── test_semantic/
│   ├── test_reasoning/
│   └── test_visualization/
│
├── examples/
│   ├── basic_analysis.py
│   ├── time_series_forecast.py
│   └── visualization_demo.py
│
└── docs/
    ├── architecture.md
    ├── api_reference.md
    └── implementation_guide.md
```

---

## 6. Implementation Priority

### Phase 1: Foundation (Week 1)
1. **Type definitions** (`types.py`)
2. **Sandbox executor** - Basic Python execution
3. **Config management** - Default packages, limits

### Phase 2: Core Logic (Week 2)
4. **Semantic layer** - Basic actions (query_data)
5. **Reasoning framework** - CoT implementation
6. **Basic visualization** - matplotlib support

### Phase 3: Advanced Features (Week 3)
7. **ToT reasoning** - Tree exploration
8. **Self-reflection** - Result verification
9. **Interactive plots** - Plotly support

### Phase 4: Polish (Week 4)
10. **Error handling** - Robust retry logic
11. **Logging** - Execution tracing
12. **Tests** - Unit + integration tests

---

## 7. Configuration Defaults

```python
# Default allowed packages
DEFAULT_PACKAGES = [
    "pandas", "numpy", "scipy", "statsmodels",
    "sklearn", "prophet",
    "matplotlib", "plotly", "seaborn",
    "json", "datetime", "math", "re"
]

# Default execution limits
DEFAULT_TIMEOUT = 30        # seconds
DEFAULT_MEMORY = 512        # MB
DEFAULT_MAX_OUTPUT = 10_000 # characters
```

---

## 8. Security Considerations

1. **Code validation** - Block dangerous operations (os, sys, subprocess)
2. **Resource limits** - Prevent DoS via timeout/memory limits
3. **No persistence** - Sandbox is ephemeral
4. **Output sanitization** - Filter sensitive data from logs
5. **Audit logging** - Track all executions for debugging

---

## 9. Extension Points

- Add custom semantic actions via registry
- Implement custom data source adapters
- Extend with additional chart templates
- Add custom reasoning strategies
- Support for R/SQL execution (future)