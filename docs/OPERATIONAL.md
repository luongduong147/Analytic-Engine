# Analytic Engine Agent - Huong Dan Van Hanh

## Tong Quan Du An

**Analytic Engine Agent** la mot module phan tich du lieu duoc cung cap boi AI, cho phep cac LLM thuc hien phan tich du lieu, du bao va truc quan hoa thong qua moi truong sandbox bao mat voi truy cap du lieu nguyen sematic va kha nang suy luan nhieu buoc.

**Cong nghe su dung:**
- **Ngon ngu**: Python 3.10+
- **Xu ly du lieu**: pandas, numpy, scipy, statsmodels
- **Machine Learning**: scikit-learn, prophet
- **Truc quan hoa**: matplotlib, plotly, seaborn
- **Tich hop LLM**: google-generativeai (Gemini)

---

## Tong Quan Kien Truc

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        ANALYTIC ENGINE AGENT                                │
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

---

## Thanh Phan 1: Sandbox

Thuc thi ma Python trong moi truong biet lap.

### Cau Truc File

```
sandbox/
├── __init__.py          # Exports
├── executor.py          # Thuc thi ma
├── manager.py           # Quan ly phien
├── security.py         # Kiem tra bao mat
└── packages.py          # Quan ly goi
```

### Cac Class va Ham

#### CodeExecutor (`executor.py`)

```python
class CodeExecutor:
    """Thuc thi ma Python trong moi truong biet lap"""
    
    DANGEROUS_IMPORTS = [
        "os", "sys", "subprocess", "socket", "requests", "urllib",
        "http", "ftplib", "smtplib", "pty", "importlib", "builtins",
        "exec", "eval", "compile",
    ]
```

| Phuong thuc | Mo ta |
|-------------|-------|
| `__init__(config: ExecutionConfig)` | Khoi tao voi cau hinh thuc thi |
| `validate_code(code: str) -> tuple[bool, Optional[str]]` | Kiem tra cac import/phep toan nguy hiem |
| `execute(code: str, context: dict) -> ExecutionResult` | Thuc thi ma voi context duoc tiem |
| `_execute_isolated(code: str) -> Any` | Chay ma trong subprocess voi timeout |

**Luong Logic:**
1. Kiem tra ma voi cac import nguy hiem
2. Tiem bien context vao ma
3. Thuc thi trong subprocess biet lap
4. Bat stdout/stderr
5. Tra ve ket qua hoac loi

---

#### SecurityValidator (`security.py`)

```python
class SecurityValidator:
    """Kiem tra ma cho cac van de bao mat"""
    
    DANGEROUS_PATTERNS = [
        # Import modules: os, sys, subprocess, socket, etc.
        (r"import\s+os\b", "Module 'os' khong duoc phep"),
        # Ma dong: eval, exec, compile
        (r"\beval\s*\(", "eval() khong duoc phep"),
        # Import tuong doi
        (r"import\s+\.", "Import tuong doi khong duoc phep"),
    ]
    
    FILE_ACCESS_PATTERNS = [
        (r"open\s*\([^)]*['\"][wr][a-z]*['\"]", "Ghi file khong duoc phep"),
        (r"\bwrite\s*\(", "Ghi file khong duoc phep"),
    ]
    
    NETWORK_PATTERNS = [
        (r"socket\s*\.\s*connect", "Ket noi mang khong duoc phep"),
        (r"requests\.get", "Yeu cau mang khong duoc phep"),
    ]
```

| Phuong thuc | Mo ta |
|-------------|-------|
| `__init__()` | Bien dich regex patterns khi khoi tao |
| `validate(code: str) -> Tuple[bool, List[str]]` | Kiem tra tat ca patterns, tra ve loi |
| `_check_patterns(code: str, patterns: List) -> List[str]` | Kiem tra pattern noi bo |
| `is_code_safe(code: str) -> bool` | Kiem tra nhanh |

---

#### SandboxSecurity (`security.py`)

```python
class SandboxSecurity:
    """Cau hinh bao mat cho sandbox"""
    
    ALLOWED_BUILTINS = [
        "print", "len", "str", "int", "float", "bool",
        "list", "dict", "tuple", "set", "range",
        "enumerate", "zip", "map", "filter",
        "sum", "min", "max", "abs", "round",
        "sorted", "reversed", "type", "isinstance",
        "hasattr", "getattr", "input",
    ]
    
    BLOCKED_ATTRIBUTES = [
        "__import__", "__builtins__", "__class__",
        "__dict__", "__module__",
    ]
```

| Phuong thuc | Mo ta |
|-------------|-------|
| `__init__()` | Khoi tao voi SecurityValidator |
| `get_restricted_globals() -> dict` | Lay globals bi han che cho exec |
| `validate_and_get_errors(code: str) -> Tuple[bool, List[str]]` | Uy thac cho validator |

---

#### PackageManager (`packages.py`)

```python
DEFAULT_PACKAGES = [
    "pandas", "numpy", "scipy", "statsmodels", "sklearn", "prophet",
    "matplotlib", "plotly", "seaborn",
    "json", "datetime", "math", "re",
]

PACKAGE_ALIASES = {
    "np": "numpy", "pd": "pandas", "plt": "matplotlib",
    "sns": "seaborn", "sklearn": "scikit-learn",
}

class PackageManager:
    """Quan ly cac goi duoc phep trong sandbox"""
```

| Phuong thuc | Mo ta |
|-------------|-------|
| `__init__(packages: List[str])` | Khoi tao voi cac goi duoc phep |
| `is_allowed(package_name: str) -> bool` | Kiem tra goi co duoc phep khong |
| `get_allowed_imports() -> str` | Tao cau lenh import |
| `add_package(package: str)` | Them goi vao danh sach trang |
| `remove_package(package: str)` | Xoa goi khoi danh sach trang |
| `allowed_packages -> List[str]` | Property: lay danh sach da sap xep |

---

#### SandboxManager (`manager.py`)

```python
@dataclass
class SandboxSession:
    session_id: str
    created_at: float
    execution_count: int
    is_active: bool
    metadata: Dict[str, Any]

@dataclass
class SandboxStats:
    total_executions: int
    successful_executions: int
    failed_executions: int
    total_execution_time: float
    active_sessions: int

class SandboxManager:
    """Quan ly moi truong thuc thi sandbox"""
```

| Phuong thuc | Mo ta |
|-------------|-------|
| `create_session(metadata: dict) -> str` | Tao phien moi, tra ve ID |
| `get_session(session_id: str) -> SandboxSession` | Lay phien theo ID |
| `execute(code, context, session_id, timeout) -> ExecutionResult` | Thuc thi voi kiem tra bao mat |
| `execute_with_session(code, context, metadata) -> tuple` | Thuc thi voi phien moi |
| `close_session(session_id: str) -> bool` | Danh dau phien khong hoat dong |
| `get_stats() -> SandboxStats` | Lay thong ke thuc thi |
| `list_sessions() -> List[SandboxSession]` | Liet ke cac phien hoat dong |
| `cleanup_stale_sessions(max_age_seconds) -> int` | Xoa cac phien cu |

**Luong Logic:**
1. Lay semaphore (gioi han thuc thi dong thoi)
2. Kiem tra ma voi SecurityValidator
3. Thuc thi voi CodeExecutor
4. Cap nhat thong ke
5. Tra ve ket qua

---

### Vi Du Su Dung

```python
from analytic_engine.sandbox import SandboxManager, ExecutionConfig

config = ExecutionConfig(timeout=30, memory_limit=512)
manager = SandboxManager(config=config, max_concurrent=5)

# Thuc thi ma
result = manager.execute(
    code="""
import pandas as pd
df = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})
print(df.sum().to_dict())
""",
    context={"user_id": "test"}
)

if result.success:
    print(result.output)  # {'a': 6, 'b': 15}
else:
    print(result.error)
```

---

## Thanh Phan 2: Semantic Layer

Layer truy cap du lieu voi cac hanh dong nguyen sematic.

### Cau Truc File

```
semantic/
├── __init__.py
├── registry.py          # Dang ky hanh dong
├── actions.py           # Hanh dong built-in
├── adapters.py         # Adapter nguon du lieu
└── transform.py       # Chuyen doi ket qua
```

### Cac Class va Ham

#### SemanticActionRegistry (`registry.py`)

```python
class SemanticActionRegistry:
    """Dang ky cac hanh dong nguyen sematic ma agents co the goi"""
```

| Phuong thuc | Mo ta |
|-------------|-------|
| `register(name: str, handler: Callable)` | Dang ky hanh dong voi handler |
| `execute(action_name: str, params: dict) -> Any` | Thuc thi hanh dong da dang ky |
| `list_actions() -> list` | Liet ke tat ca ten hanh dong |
| `get_action(name: str) -> Callable` | Lay handler hanh dong |

---

#### Built-in Actions (`actions.py`)

```python
def create_builtin_actions(data_accessor: Callable = None) -> Dict[str, Callable]:
```

| Hanh dong | Tham so | Mo ta |
|-----------|---------|-------|
| `query_data` | `source, filters, columns, limit` | Truy van du lieu tu nguon |
| `fetch_metrics` | `metric_names, timeframe` | Lay cac chi so cu the |
| `get_historical_data` | `entity, start_date, end_date` | Lay du lieu lich su |
| `get_aggregated` | `source, agg_func, group_by` | Lay du lieu tong hop |

---

#### DataSourceAdapter (`adapters.py`)

```python
class DataSourceAdapter(ABC):
    """Lop co so truu tuong cho cac adapter nguon du lieu"""
    
    @abstractmethod
    def query(self, source: str, filters, columns, limit) -> pd.DataFrame:
        pass
    
    @abstractmethod
    def get_schema(self, source: str) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        pass
```

| Class | Mo ta |
|-------|-------|
| `DataSourceAdapter` | Lop co so truu tuong cho nguon du lieu |
| `MockDataAdapter` | Adapter mock cho viec test |
| `DataSourceManager` | Quan ly nhieu adapter |

---

#### ResultTransformer (`transform.py`)

```python
class ResultTransformer:
    """Chuyen doi ket qua truy van sang dinh dang chuan"""
```

| Phuong thuc | Mo ta |
|-------------|-------|
| `to_dict(data: Any) -> Dict` | Chuyen doi sang dictionary |
| `to_json(data: Any) -> str` | Chuyen doi sang chuoi JSON |
| `to_csv(data: Any) -> str` | Chuyen doi sang chuoi CSV |
| `filter_columns(data, columns) -> DataFrame` | Loc cac cot |
| `apply_filters(data, filters) -> DataFrame` | Ap dung loc hang |

---

### Vi Du Su Dung

```python
from analytic_engine.semantic import SemanticActionRegistry, create_builtin_actions

registry = SemanticActionRegistry()

# Dang ky cac hanh dong built-in
actions = create_builtin_actions()
for name, handler in actions.items():
    registry.register(name, handler)

# Thuc thi hanh dong
result = registry.execute("query_data", {
    "source": "sales",
    "limit": 10
})
```

---

## Thanh Phan 3: Reasoning Framework

Suy luan nhieu buoc voi tu kiem tra.

### Cau Truc File

```
reasoning/
├── __init__.py
├── orchestrator.py      # Dieu phoi chinh
├── chain.py             # Cau truc CoT
├── tree.py             # Cau truc ToT
├── reflector.py         # Tu phan chieu
└── verifier.py          # Xac minh ket qua
```

### Cac Class va Ham

#### ReasoningOrchestrator (`orchestrator.py`)

```python
class ReasoningOrchestrator:
    """Dieu phoi chinh cho framework suy luan"""
```

| Phuong thuc | Mo ta |
|-------------|-------|
| `__init__(semantic_registry, executor)` | Khoi tao voi cac phu thuoc |
| `reason(request: AnalysisRequest) -> List[ThoughtStep]` | Thuc thi suy luan |
| `reflect(steps: List[ThoughtStep]) -> ReflectionResult` | Phan chieu tren cac buoc |
| `verify(result, constraints) -> VerificationResult` | Xac minh theo rang buoc |
| `execute_with_verification(request, max_retries) -> AnalysisResult` | Thuc thi voi thu lai |

---

#### ChainOfThought (`chain.py`)

```python
class ChainOfThought:
    """Cau truc suy luan Chain of Thought"""
```

| Phuong thuc | Mo ta |
|-------------|-------|
| `__init__(semantic_registry, executor)` | Khoi tao |
| `reason(request: AnalysisRequest) -> List[ThoughtStep]` | Thuc thi suy luan tuan tu |
| `_analyze_step(step_num, context) -> str` | Phan tich buoc hien tai |
| `_determine_action(thought) -> tuple` | Xac dinh hanh dong tiep theo |
| `_execute_action(action, params) -> Any` | Thuc thi hanh dong |
| `_is_complete(step, all_steps) -> bool` | Kiem tra hoan thanh |

**Luong Logic:**
```
Cho moi buoc:
  1. Phan tich buoc -> tao thought
  2. Xac dinh hanh dong -> chon hanh dong nguyen sematic
  3. Thuc thi hanh dong -> lay ket qua
  4. Tao ThoughtStep -> them vao trace
  5. Kiem tra hoan thanh -> break neu xong
```

---

#### TreeOfThought (`tree.py`)

```python
@dataclass
class ThoughtTreeNode:
    step: ThoughtStep
    depth: int
    children: List["ThoughtTreeNode"]
    score: float

class TreeOfThought:
    """Cau truc suy luan Tree of Thought"""
```

| Phuong thuc | Mo ta |
|-------------|-------|
| `reason(request) -> List[ThoughtStep]` | Thuc thi suy luan cay |
| `_expand_tree(node, request, depth)` | Mo rong nhanh cay |
| `_generate_branches(step, depth) -> List` | Tao cac nhanh |
| `_find_best_path(root) -> List[ThoughtStep]` | Tim duong tot nhat theo diem |

**Luong Logic:**
```
1. Tao nut goc
2. Mo rong cay de quy:
   - Tao nhanh tai moi do sau
   - Gan diem cho cac nhanh
   - Tiep tuc den khi max_depth
3. Tim duong tot nhat (tong confidence lon nhat)
4. Tra ve duong tot nhat lai ThoughtSteps
```

---

#### SelfReflector (`reflector.py`)

```python
class SelfReflector:
    """Kha nang tu phan chieu cho suy luan"""
```

| Phuong thuc | Mo t |

| `reflect(steps) -> ReflectionResult` | Danh gia chat luong suy luan |
| `analyze_errors(steps) -> Dict` | Phan tich cac mau loi |
| `suggest_improvements(steps) -> List[str]` | De xuat cac cai tien |

**Logic Phan chieu:**
- Kiem tra cac buoc confidence thap (< threshold)
- Kiem tra cac hanh dong that bai (khong co ket qua)
- Tinh trung binh confidence
- Xac dinh co can thu lai hay khong

---

#### VerificationEngine (`verifier.py`)

```python
class VerificationEngine:
    """Xac minh ket qua suy luan theo rang buoc"""
```

| Phuong thuc | Mo ta |
|-------------|-------|
| `verify(result, constraints) -> VerificationResult` | Xac minh theo rang buoc |
| `_check_type(result, expected) -> bool` | Kiem tra kieu |
| `verify_reasoning_steps(steps) -> VerificationResult` | Xac minh tinh lien ket buoc |
| `verify_data_constraints(data, constraints) -> VerificationResult` | Xac minh du lieu |

**Cac Rang buoc:**
| Key | Mo ta |
|-----|-------|
| `expected_type` | Kieu ket qua mong doi |
| `min_value` | Gia tri so thap nhat |
| `max_value` | Gia tri so cao nhat |
| `allowed_values` | Danh sach cac gia tri duoc phep |
| `max_length` | Do dai toi da |
| `not_empty` | Du lieu khong duoc rong |
| `min_rows` | So hang toi thieu |
| `required_columns` | Ten cot bat buoc |

---

### Vi Du Su Dung

```python
from analytic_engine import AnalyticEngineAgent
from analytic_engine.types import AnalysisRequest, ReasoningMode

agent = AnalyticEngineAgent()

request = AnalysisRequest(
    objective="Phan tich doanh thu theo thang",
    reasoning_mode=ReasoningMode.CHAIN_OF_THOUGHT,
    max_steps=5,
    context={"data": df}
)

result = agent.analyze(request)
print(result.answer)
print(result.confidence)
```

---

## Thanh Phan 4: Visualization Engine

Tao bieu do va dinh dau ra.

### Cau Truc File

```
visualization/
├── __init__.py
├── engine.py            # Tao bieu do
├── templates.py         # Mau bieu do
└── formatters.py        # Dinh dang dau ra
```

### Cac Class va Ham

#### VisualizationEngine (`engine.py`)

```python
class VisualizationEngine:
    """Tao bieu do va truc quan hoa"""
    
    CHART_METHODS = {
        ChartType.LINE: "_line_chart",
        ChartType.BAR: "_bar_chart",
        ChartType.SCATTER: "_scatter_chart",
        ChartType.PIE: "_pie_chart",
        ChartType.HISTOGRAM: "_histogram",
        ChartType.BOX: "_box_plot",
        ChartType.HEATMAP: "_heatmap",
    }
```

| Phuong thuc | Mo ta |
|-------------|-------|
| `generate(data, chart_type, config) -> VisualizationResult` | Tao bieu do |
| `_line_chart(data, config) -> Any` | Tao bieu do duong |
| `_bar_chart(data, config) -> Any` | Tao bieu do cot |
| `_scatter_chart(data, config) -> Any` | Tao bieu do phan tan |
| `_pie_chart(data, config) -> Any` | Tao bieu do tron |
| `_histogram(data, config) -> Any` | Tao bieu do tan suat |
| `_box_plot(data, config) -> Any` | Tao bieu do hop |
| `_heatmap(data, config) -> Any` | Tao bieu do nhiet |
| `_to_display_format(figure, format) -> str` | Chuyen doi sang dinh dang hien thi |

**Cac Lua chon Cau hinh:**
| Key | Mo ta |
|-----|-------|
| `x` | Cot truc x |
| `y` | Cot truc y |
| `interactive` | Su dung plotly (True/False) |
| `format` | Dinhdang dau ra (png/html) |
| `bins` | So bins (histogram) |
| `column` | Cot cho bieu do mot cot |

---

#### TemplateLibrary (`templates.py`)

```python
@dataclass
class ChartTemplate:
    name: str
    chart_type: str
    required_config: list
    render_func: Optional[Callable]
```

| Mau | Loai bieu do | Mo ta |
|-----|--------------|-------|
| `trends` | line | Xu huong chuoi thoi gian |
| `comparison` | bar | So sanh gia tri theo danh muc |
| `distribution` | histogram | Phan bo du lieu |
| `correlation` | heatmap | Ma tran tuong quan |
| `proportion` | pie | Ti le cac phan |
| `outliers` | box | Bieu do hop phat hien ngoai lai |
| `scatter` | scatter | Bieu do phan tan XY |

| Phuong thuc | Mo ta |
|-------------|-------|
| `get_template(name) -> Optional[Dict]` | Lay mau theo ten |
| `list_templates() -> list` | Liet ke tat ca mau |
| `apply_template(name, config) -> Dict` | Tron mau voi cau hinh |

---

#### OutputFormatter (`formatters.py`)

```python
class OutputFormatter:
    """Dinh dau truc quan hoa cho hien thi"""
```

| Phuong thuc | Mo ta |
|-------------|-------|
| `to_base64_png(figure) -> str` | Chuyen doi sang base64 PNG |
| `to_html(figure) -> str` | Chuyen doi sang HTML |
| `to_json(figure) -> str` | Chuyen doi sang JSON |
| `format_for_display(figure, format) -> Dict` | Dinh dau cho hien thi |
| `wrap_in_html(content, title) -> str` | Bao trong template HTML |

---

### Vi Du Su Dung

```python
from analytic_engine import AnalyticEngineAgent
from analytic_engine.types import ChartType

agent = AnalyticEngineAgent()

# Tao truc quan hoa
result = agent.visualize(
    data=df,
    chart_type="bar",
    config={
        "x": "category",
        "y": "value",
        "interactive": True
    }
)

# result.data chua base64 PNG hoac HTML
```

---

## Tom Tat Luong Du Lieu

```
1. YEU CAU
   User/LLM gui yeu cau phan tich
           │
           ▼
2. SUY LUAN
   Framework suy luan phan tich yeu cau
   - Phan ra thanh cac buoc
   - Xac dinh du lieu can thiet
   - Ke hoach thuc thi
           │
           ▼
3. LAY DU LIEU (Semantic Layer)
   Goi hanh dong nguyen sematic lay du lieu
   - Giai quyet nguon du lieu
   - Ap dung bo loc
   - Tra ve du lieu cau truc
           │
           ▼
4. THUC THI (Sandbox)
   Thuc thi ma phan tich
   - Viet ma vao sandbox
   - Chay voi gioi han tai nguyen
   - Bat loi/ket qua
           │
           ▼
5. XAC MINH (Reasoning)
   Tu phan chieu ket qua
   - Kiem tra tinh dung dan
   - Xac minh rang buoc
   - Thu lai neu can
           │
           ▼
6. TRUC QUAN HOA
   Tao bieu do
   - Tao bieu do matplotlib/plotly
   - Chuyen doi sang dinh dang hien thi
           │
           ▼
7. TRA LOI
   Tra ve ket qua + truc quan hoa
```

---

## Diem Mo Rong

- **Hanh dong nguyen sematic tuychinh**: Dang ky qua `SemanticActionRegistry.register()`
- **Nguon du lieu tuychinh**: Cau lenh `DataSourceAdapter`
- **Mau bieu do tuychinh**: Them vao `TemplateLibrary.TEMPLATES`
- **Che do suy luan tuychinh**: Mo rong `ReasoningOrchestrator`
- **Loai bieu do them**: Them vao `VisualizationEngine.CHART_METHODS`
