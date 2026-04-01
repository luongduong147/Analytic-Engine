# Plan Triển Khai: Function LLM Reasoning

## 1. Overview

**Mục tiêu**: Xây dựng hybrid reasoning system cho Analytic Engine Agent, kết hợp prompt-based reasoning (cho simple queries) và tool-based LLM reasoning (cho complex queries).

**Philosophy**:
- **Simple queries**: Thống kê mô tả, visualize chart đơn giản → Prompt-based reasoning
- **Complex queries**: Metric definition, diagnostic analysis, forecasting → Tool-based LLM reasoning (bắt buộc có LLM)

---

## 2. Architecture

```
User Query
     │
     ▼
┌──────────────────────────────────────────┐
│  QueryClassifier (Gemini 2.0 Flash)      │
│                                          │
│  Classification: SIMPLE / COMPLEX        │
│  Confidence score                       │
└────────────────────┬─────────────────────┘
                     │
        ┌────────────┴────────────┐
        ▼                         ▼
┌──────────────────┐   ┌──────────────────┐
│   Simple Path    │   │   Complex Path   │
│                  │   │                  │
│ Prompt-based     │   │ Tool-based       │
│ Reasoning        │   │ LLM Reasoning    │
│ (trong agent     │   │ (CoT/ToT với     │
│  prompt)         │   │  Gemini LLM)     │
└──────────────────┘   └──────────────────┘
```

---

## 3. Phase Details

### Phase 1: Query Classifier

**Mục đích**: Phân loại query thành SIMPLE hoặc COMPLEX sử dụng Gemini 2.0 Flash.

**Files tạo mới**:
- `src/analytic_engine/reasoning/classifier.py`

**Classes/Functions**:

```python
# classifier.py

from dataclasses import dataclass
from enum import Enum
from typing import Optional
import google.generativeai as genai

class QueryComplexity(Enum):
    SIMPLE = "simple"      # Thống kê mô tả, visualize chart đơn giản
    COMPLEX = "complex"    # Metric definition, diagnostic, forecasting

@dataclass
class ClassificationResult:
    complexity: QueryComplexity
    confidence: float
    reasoning: str
    recommended_approach: str  # "prompt" hoặc "tool"

class QueryClassifier:
    """Query classifier sử dụng Gemini 2.0 Flash"""
    
    def __init__(self, api_key: str, model: str = "gemini-2.0-flash"):
        self.model_name = model
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)
    
    def classify(self, query: str, context: Optional[dict] = None) -> ClassificationResult:
        """
        Phân loại query thành SIMPLE hoặc COMPLEX
        
        Args:
            query: User query
            context: Optional context (user_info, project_info)
        
        Returns:
            ClassificationResult với complexity, confidence, reasoning
        """
        # Prompt cho classifier
        classification_prompt = f"""
Bạn là một query classifier cho hệ thống phân tích dữ liệu.

Hãy phân loại câu hỏi sau thành SIMPLE hoặc COMPLEX:

## Câu hỏi:
{query}

## Context:
{context if context else "Không có context"}

## Định nghĩa:

**SIMPLE** - Các truy vấn thống kê mô tả đơn giản:
- Tổng số lượng (count, sum)
- Trung bình (mean, average)
- Phân bố cơ bản (distribution)
- Visualize chart đơn giản (bar, pie, line)
- Không cần tính toán phức tạp

**COMPLEX** - Các truy vấn phân tích nâng cao:
- Định nghĩa bộ metric mới
- Phân tích chẩn đoán (diagnostic analysis)
- Phân tích dự báo (forecasting)
- Tính toán multi-step
- So sánh, đối chiếu phức tạp
- Yêu cầu reasoning nhiều bước

## Output format (JSON):
```json
{{
  "complexity": "SIMPLE" hoặc "COMPLEX",
  "confidence": 0.0-1.0,
  "reasoning": "Giải thích ngắn gọn tại sao",
  "recommended_approach": "prompt" hoặc "tool"
}}
```

Chỉ trả về JSON, không có text khác.
"""
        response = self.model.generate_content(classification_prompt)
        return self._parse_response(response.text)
    
    def _parse_response(self, response: str) -> ClassificationResult:
        """Parse JSON response từ LLM"""
        import json
        # Extract JSON from response
        data = json.loads(response)
        return ClassificationResult(
            complexity=QueryComplexity(data["complexity"]),
            confidence=data["confidence"],
            reasoning=data["reasoning"],
            recommended_approach=data["recommended_approach"]
        )
```

**Đặc điểm**:
- Sử dụng Gemini 2.0 Flash (model name: `gemini-2.0-flash`)
- Classification prompt có định nghĩa rõ ràng về SIMPLE vs COMPLEX
- Trả về confidence score để đánh giá độ tin cậy
- Có thể disable classifier nếu cần (fallback về rule-based)

---

### Phase 2: LLM Reasoning Component

**Mục đích**: Cung cấp LLM-powered reasoning cho complex queries.

**Files tạo mới**:
- `src/analytic_engine/reasoning/components.py`

**Classes/Functions**:

```python
# components.py

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional
import google.generativeai as genai

@dataclass
class Action:
    name: str
    params: Dict[str, Any]
    reasoning: str

@dataclass
class ReasoningStep:
    step_number: int
    thought: str
    action: Optional[Action]
    result: Any
    confidence: float

class LLMReasoningComponent:
    """LLM-powered reasoning component cho complex queries"""
    
    def __init__(self, api_key: str, model: str = "gemini-2.0-flash"):
        self.model_name = model
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)
        self.max_steps = 10
    
    def reason(
        self,
        objective: str,
        available_actions: List[str],
        context: Dict[str, Any]
    ) -> List[ReasoningStep]:
        """
        Thực hiện reasoning với LLM
        
        Args:
            objective: Mục tiêu phân tích
            available_actions: List các actions có thể gọi
            context: Context data
        
        Returns:
            List các ReasoningStep
        """
        steps = []
        current_context = context.copy()
        
        for step_num in range(1, self.max_steps + 1):
            # LLM quyết định action tiếp theo
            action = self._decide_action(objective, available_actions, current_context)
            
            if action is None:
                # Không còn action phù hợp, kết thúc
                break
            
            # Execute action
            result = self._execute_action(action, current_context)
            
            step = ReasoningStep(
                step_number=step_num,
                thought=f"Step {step_num}: {action.reasoning}",
                action=action,
                result=result,
                confidence=0.8
            )
            steps.append(step)
            current_context[f"step_{step_num}"] = result
            
            # Kiểm tra done
            if self._is_complete(step, steps, objective):
                break
        
        return steps
    
    def _decide_action(
        self,
        objective: str,
        available_actions: List[str],
        context: Dict[str, Any]
    ) -> Optional[Action]:
        """LLM quyết định action tiếp theo"""
        prompt = f"""
Bạn là một reasoning engine. Hãy quyết định action tiếp theo để đạt được mục tiêu.

## Mục tiêu:
{objective}

## Available Actions:
{', '.join(available_actions)}

## Context hiện tại:
{context}

## Yêu cầu:
1. Chọn action phù hợp nhất với mục tiêu
2. Xác định parameters cần thiết
3. Giải thích ngắn gọn tại sao chọn action này

## Output format (JSON):
```json
{{
  "action_name": "tên action",
  "params": {{"key": "value"}},
  "reasoning": "Giải thích ngắn"
}}
```

Nếu không cần thêm action nào, trả về:
```json
{{
  "action_name": null,
  "params": {{}},
  "reasoning": "Hoàn thành mục tiêu"
}}
```

Chỉ trả về JSON.
"""
        response = self.model.generate_content(prompt)
        return self._parse_action_response(response.text)
    
    def _execute_action(self, action: Action, context: Dict[str, Any]) -> Any:
        """Execute action (placeholder - sẽ được wire với semantic registry)"""
        # Placeholder - sẽ được implement sau
        pass
    
    def _is_complete(
        self,
        step: ReasoningStep,
        all_steps: List[ReasoningStep],
        objective: str
    ) -> bool:
        """Kiểm tra reasoning có hoàn thành chưa"""
        if step.action is None:
            return True
        if step.action.name is None:
            return True
        return False
    
    def _parse_action_response(self, response: str) -> Optional[Action]:
        """Parse JSON response thành Action"""
        import json
        data = json.loads(response)
        if data.get("action_name") is None:
            return None
        return Action(
            name=data["action_name"],
            params=data.get("params", {}),
            reasoning=data.get("reasoning", "")
        )
```

**Đặc điểm**:
- LLM quyết định action dựa trên objective và context
- Support multi-step reasoning
- Trả về reasoning steps có thể trace được
- Có thể integrate với semantic registry để execute thực sự

---

### Phase 3: Enhanced Chain of Thought

**Mục đích**: Cải thiện CoT để sử dụng LLM cho action selection.

**Files modify**:
- `src/analytic_engine/reasoning/chain.py` (NEW FILE - thay thế hoặc mở rộng)

**Classes/Functions**:

```python
# reasoning/chain.py (enhanced version)

from typing import List, Callable, Any, Optional
from .components import LLMReasoningComponent
from .types import AnalysisRequest, ThoughtStep, ReasoningMode

class EnhancedChainOfThought:
    """Enhanced Chain of Thought với LLM support"""
    
    def __init__(
        self,
        semantic_registry: Any,
        executor: Callable,
        llm_component: Optional[LLMReasoningComponent] = None
    ):
        self.semantic = semantic_registry
        self.executor = executor
        self.llm = llm_component
        self.max_steps = 10
    
    def reason(self, request: AnalysisRequest) -> List[ThoughtStep]:
        """Execute chain of thought reasoning"""
        if self.llm is not None:
            return self._reason_with_llm(request)
        return self._reason_fallback(request)
    
    def _reason_with_llm(self, request: AnalysisRequest) -> List[ThoughtStep]:
        """Reasoning với LLM"""
        available_actions = self.semantic.list_actions()
        
        llm_steps = self.llm.reason(
            objective=request.objective,
            available_actions=available_actions,
            context=request.context
        )
        
        # Convert LLM steps to ThoughtSteps
        steps = []
        for i, llm_step in enumerate(llm_steps, 1):
            action_name = llm_step.action.name if llm_step.action else None
            params = llm_step.action.params if llm_step.action else {}
            
            result = None
            if action_name and action_name in available_actions:
                result = self.semantic.execute(action_name, params)
            
            step = ThoughtStep(
                step_number=i,
                thought=llm_step.thought,
                action=action_name or "",
                result=result,
                confidence=llm_step.confidence
            )
            steps.append(step)
        
        return steps
    
    def _reason_fallback(self, request: AnalysisRequest) -> List[ThoughtStep]:
        """Fallback reasoning không có LLM"""
        # Rule-based simple reasoning
        steps = []
        current_context = request.context.copy()
        
        for step_num in range(1, request.max_steps + 1):
            action, params = self._determine_action_fallback(
                request.objective, 
                current_context
            )
            result = self._execute_action(action, params)
            
            step = ThoughtStep(
                step_number=step_num,
                thought=f"Step {step_num}: Execute {action}",
                action=action,
                result=result
            )
            steps.append(step)
            current_context[f"step_{step_num}"] = result
            
            if self._is_complete(step, steps):
                break
        
        return steps
    
    def _determine_action_fallback(
        self, 
        objective: str, 
        context: dict
    ) -> tuple[str, dict]:
        """Rule-based action selection"""
        objective_lower = objective.lower()
        
        keywords_action_map = {
            "tổng": ("query_data", {"agg": "sum"}),
            "trung bình": ("query_data", {"agg": "mean"}),
            "số lượng": ("query_data", {"agg": "count"}),
            "phân bố": ("visualize", {"chart_type": "bar"}),
            "trend": ("fetch_metrics", {"type": "time_series"}),
            "so sánh": ("get_aggregated", {"compare": True}),
        }
        
        for keyword, (action, params) in keywords_action_map.items():
            if keyword in objective_lower:
                return action, params
        
        return ("query_data", {"limit": 100})
    
    def _execute_action(self, action: str, params: dict) -> Any:
        if action in self.semantic.list_actions():
            return self.semantic.execute(action, params)
        return None
    
    def _is_complete(self, step: ThoughtStep, all_steps: List[ThoughtStep]) -> bool:
        return len(all_steps) >= self.max_steps
```

**Đặc điểm**:
- Có LLM component → dùng LLM để quyết định action
- Không có LLM → fallback rule-based
- Giữ backward compatibility

---

### Phase 4: Enhanced Tree of Thought

**Mục đích**: Cải thiện ToT với smart branch generation.

**Files tạo mới**:
- `src/analytic_engine/reasoning/tree_enhanced.py`

**Classes/Functions**:

```python
# reasoning/tree_enhanced.py

from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from .components import LLMReasoningComponent
from .types import AnalysisRequest, ThoughtStep

@dataclass
class ThoughtTreeNode:
    step: ThoughtStep
    depth: int = 0
    children: List["ThoughtTreeNode"] = field(default_factory=list)
    score: float = 0.0

class EnhancedTreeOfThought:
    """Enhanced Tree of Thought với LLM support"""
    
    def __init__(
        self,
        cot_reasoner: Any,
        llm_component: Optional[LLMReasoningComponent] = None,
        max_branches: int = 3,
        max_depth: int = 5
    ):
        self.cot = cot_reasoner
        self.llm = llm_component
        self.max_branches = max_branches
        self.max_depth = max_depth
    
    def reason(self, request: AnalysisRequest) -> List[ThoughtStep]:
        """Execute tree of thought reasoning"""
        root = ThoughtTreeNode(
            ThoughtStep(
                step_number=0,
                thought=request.objective,
                action="start",
                result=None
            )
        )
        
        self._expand_tree(root, request, current_depth=0)
        
        best_path = self._find_best_path(root)
        return best_path
    
    def _expand_tree(
        self,
        node: ThoughtTreeNode,
        request: AnalysisRequest,
        current_depth: int
    ) -> None:
        """Expand tree với branches"""
        if current_depth >= self.max_depth:
            return
        
        branches = self._generate_branches_smart(
            node.step,
            current_depth,
            request.objective
        )
        
        for branch_action in branches[:self.max_branches]:
            child_step = ThoughtStep(
                step_number=current_depth + 1,
                thought=branch_action["thought"],
                action=branch_action["action"],
                result=branch_action.get("result")
            )
            child_node = ThoughtTreeNode(child_step, current_depth + 1)
            child_node.score = branch_action.get("score", 0.5)
            node.add_child(child_node)
            
            self._expand_tree(child_node, request, current_depth + 1)
    
    def _generate_branches_smart(
        self,
        current_step: ThoughtStep,
        depth: int,
        objective: str
    ) -> List[Dict[str, Any]]:
        """Generate branches sử dụng LLM"""
        if self.llm is not None:
            return self._generate_branches_with_llm(current_step, depth, objective)
        return self._generate_branches_fallback(depth)
    
    def _generate_branches_with_llm(
        self,
        current_step: ThoughtStep,
        depth: int,
        objective: str
    ) -> List[Dict[str, Any]]:
        """LLM generates multiple branches"""
        prompt = f"""
Bạn là một reasoning engine. Hãy generate các branches tiếp theo để đạt được mục tiêu.

## Mục tiêu:
{objective}

## Current Step:
{current_step.action} - {current_step.thought}

## Depth hiện tại:
{depth}

## Yêu cầu:
1. Tạo 3-5 branches khác nhau để tiến tới mục tiêu
2. Mỗi branch cần có: action name, thought, score (0-1)
3. Các branches nên explore different approaches

## Output format (JSON):
```json
[
  {{
    "action": "query_data",
    "thought": "Mô tả branch",
    "score": 0.8
  }},
  ...
]
```

Chỉ trả về JSON.
"""
        response = self.llm.model.generate_content(prompt)
        return self._parse_branches_response(response.text)
    
    def _generate_branches_fallback(self, depth: int) -> List[Dict[str, Any]]:
        """Fallback branch generation"""
        actions = ["query_data", "fetch_metrics", "get_aggregated", "analyze"]
        branches = []
        
        for action in actions[:self.max_branches]:
            branches.append({
                "thought": f"Explore {action} at depth {depth}",
                "action": action,
                "score": 1.0 / (depth + 1)
            })
        
        return branches
    
    def _parse_branches_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse JSON response thành branches"""
        import json
        return json.loads(response)
    
    def _find_best_path(self, root: ThoughtTreeNode) -> List[ThoughtStep]:
        """Find best scoring path"""
        paths = root.get_all_paths()
        if not paths:
            return [root.step]
        
        best = max(paths, key=lambda p: sum(s.confidence for s in p if s.confidence))
        return best
```

**Đặc điểm**:
- Có LLM → smart branch generation
- Không có LLM → fallback basic branches
- Smart scoring dựa trên objective relevance

---

### Phase 5: Integration - Orchestrator Update

**Mục đích**: Wire classifier vào orchestrator, route đến đúng handler.

**Files tạo mới**:
- `src/analytic_engine/reasoning/router.py`

**Classes/Functions**:

```python
# reasoning/router.py

from dataclasses import dataclass
from typing import Optional, Dict, Any
from .classifier import QueryClassifier, QueryComplexity, ClassificationResult
from .components import LLMReasoningComponent
from .chain import EnhancedChainOfThought
from .tree_enhanced import EnhancedTreeOfThought
from .types import AnalysisRequest, ThoughtStep

@dataclass
class ReasoningResult:
    steps: List[ThoughtStep]
    reasoning_type: str  # "prompt" hoặc "tool"
    classification: ClassificationResult

class ReasoningRouter:
    """Router để route query đến đúng reasoning approach"""
    
    def __init__(
        self,
        classifier: QueryClassifier,
        llm_component: Optional[LLMReasoningComponent] = None,
        cot_reasoner: Optional[EnhancedChainOfThought] = None,
        tot_reasoner: Optional[EnhancedTreeOfThought] = None
    ):
        self.classifier = classifier
        self.llm = llm_component
        self.cot = cot_reasoner
        self.tot = tot_reasoner
    
    def route(
        self,
        request: AnalysisRequest,
        context: Optional[Dict[str, Any]] = None
    ) -> ReasoningResult:
        """
        Route query đến đúng reasoning approach
        
        Args:
            request: Analysis request
            context: Optional context info
        
        Returns:
            ReasoningResult với steps và metadata
        """
        # Step 1: Classify query
        classification = self.classifier.classify(request.objective, context)
        
        # Step 2: Route based on classification
        if classification.complexity == QueryComplexity.SIMPLE:
            return self._handle_simple(request, classification)
        else:
            return self._handle_complex(request, classification)
    
    def _handle_simple(
        self,
        request: AnalysisRequest,
        classification: ClassificationResult
    ) -> ReasoningResult:
        """
        Handle simple query - prompt-based reasoning
        Note: Logic này sẽ ở LangChain agent layer, không phải trong module
        """
        return ReasoningResult(
            steps=[],
            reasoning_type="prompt",
            classification=classification
        )
    
    def _handle_complex(
        self,
        request: AnalysisRequest,
        classification: ClassificationResult
    ) -> ReasoningResult:
        """Handle complex query - tool-based LLM reasoning"""
        # Sử dụng CoT hoặc ToT
        if request.reasoning_mode.value == "ToT" and self.tot:
            steps = self.tot.reason(request)
        elif self.cot:
            steps = self.cot.reason(request)
        else:
            # Fallback
            steps = self._fallback_reasoning(request)
        
        return ReasoningResult(
            steps=steps,
            reasoning_type="tool",
            classification=classification
        )
    
    def _fallback_reasoning(self, request: AnalysisRequest) -> List[ThoughtStep]:
        """Fallback reasoning"""
        return [
            ThoughtStep(
                step_number=1,
                thought="Fallback reasoning",
                action="query_data",
                result=None
            )
        ]
```

---

### Phase 6: Updated Orchestrator

**Mục đích**: Cập nhật orchestrator để sử dụng router.

**Files tạo mới**:
- `src/analytic_engine/reasoning/orchestrator_v2.py`

**Classes/Functions**:

```python
# reasoning/orchestrator_v2.py

from typing import List, Optional, Dict, Any
from .router import ReasoningRouter, ReasoningResult
from .reflector import SelfReflector
from .verifier import VerificationEngine
from .classifier import QueryClassifier
from .components import LLMReasoningComponent
from .chain import EnhancedChainOfThought
from .tree_enhanced import EnhancedTreeOfThought
from .types import AnalysisRequest, AnalysisResult, ThoughtStep, ReasoningMode

class ReasoningOrchestratorV2:
    """Enhanced orchestrator với classifier và router"""
    
    def __init__(
        self,
        classifier: QueryClassifier,
        llm_component: Optional[LLMReasoningComponent] = None,
        semantic_registry: Optional[Any] = None,
        executor: Optional[Callable] = None
    ):
        self.classifier = classifier
        self.llm = llm_component
        
        # Initialize reasoning components
        cot = None
        tot = None
        
        if semantic_registry and executor and llm_component:
            cot = EnhancedChainOfThought(semantic_registry, executor, llm_component)
            tot = EnhancedTreeOfThought(cot, llm_component)
        elif semantic_registry and executor:
            cot = EnhancedChainOfThought(semantic_registry, executor)
            tot = EnhancedTreeOfThought(cot)
        
        self.router = ReasoningRouter(
            classifier=classifier,
            llm_component=llm_component,
            cot_reasoner=cot,
            tot_reasoner=tot
        )
        
        self.reflector = SelfReflector()
        self.verifier = VerificationEngine()
    
    def reason(
        self,
        request: AnalysisRequest,
        context: Optional[Dict[str, Any]] = None
    ) -> List[ThoughtStep]:
        """Execute reasoning với classification"""
        result = self.router.route(request, context)
        return result.steps
    
    def reason_with_verification(
        self,
        request: AnalysisRequest,
        max_retries: int = 3,
        context: Optional[Dict[str, Any]] = None
    ) -> AnalysisResult:
        """Execute reasoning with verification and retry"""
        attempts = []
        
        for attempt in range(max_retries):
            result = self.router.route(request, context)
            steps = result.steps
            reflection = self.reflector.reflect(steps)
            
            if reflection.is_valid or attempt == max_retries - 1:
                return AnalysisResult(
                    answer=f"Analysis completed with {len(steps)} steps",
                    data=steps[-1].result if steps else None,
                    reasoning_trace=steps,
                    confidence=reflection.confidence,
                    errors=reflection.issues if not reflection.is_valid else []
                )
            
            attempts.append({"steps": steps, "reflection": reflection})
        
        return AnalysisResult(
            answer="Analysis failed after maximum retries",
            reasoning_trace=attempts[-1]["steps"] if attempts else [],
            confidence=0.0,
            errors=["Max retries exceeded"]
        )
```

---

### Phase 7: Export Updates

**Files modify**:
- `src/analytic_engine/reasoning/__init__.py`

```python
# reasoning/__init__.py

from .classifier import QueryClassifier, QueryComplexity, ClassificationResult
from .components import LLMReasoningComponent, Action, ReasoningStep
from .chain import EnhancedChainOfThought
from .tree_enhanced import EnhancedTreeOfThought
from .router import ReasoningRouter, ReasoningResult
from .orchestrator_v2 import ReasoningOrchestratorV2

__all__ = [
    "QueryClassifier",
    "QueryComplexity", 
    "ClassificationResult",
    "LLMReasoningComponent",
    "Action",
    "ReasoningStep",
    "EnhancedChainOfThought",
    "EnhancedTreeOfThought",
    "ReasoningRouter",
    "ReasoningResult",
    "ReasoningOrchestratorV2",
]
```

---

## 4. File Structure After Implementation

```
src/analytic_engine/
├── __init__.py
├── agent.py                 # Không đụng đến
├── config.py               # Không đụng đến
├── types.py                # Không đụng đến
├── reasoning/
│   ├── __init__.py         # MODIFIED: thêm exports
│   ├── orchestrator.py     # Không đụng đến (giữ nguyên)
│   ├── chain.py            # NEW: EnhancedChainOfThought (file mới)
│   ├── tree.py             # Không đụng đến
│   ├── tree_enhanced.py    # NEW: EnhancedTreeOfThought
│   ├── classifier.py       # NEW: QueryClassifier
│   ├── components.py       # NEW: LLMReasoningComponent
│   ├── router.py           # NEW: ReasoningRouter
│   ├── orchestrator_v2.py  # NEW: ReasoningOrchestratorV2
│   ├── reflector.py        # Không đụng đến
│   └── verifier.py         # Không đụng đến
├── sandbox/                # Không đụng đến
├── semantic/               # Không đụng đến
└── visualization/          # Không đụng đến
```

---

## 5. Dependencies

**Thêm vào `requirements.txt`**:
```
google-generativeai>=0.3.0
```

---

## 6. Implementation Order

| Phase | Files | Priority |
|-------|-------|----------|
| 1 | `classifier.py` | 1 |
| 2 | `components.py` | 2 |
| 3 | `chain.py` | 3 |
| 4 | `tree_enhanced.py` | 4 |
| 5 | `router.py` | 5 |
| 6 | `orchestrator_v2.py` | 6 |
| 7 | `__init__.py` | 7 |

---

## 7. Usage Example

```python
# Khởi tạo
from analytic_engine.reasoning import (
    QueryClassifier,
    LLMReasoningComponent,
    ReasoningOrchestratorV2
)

# Setup
classifier = QueryClassifier(api_key="GEMINI_API_KEY")
llm_component = LLMReasoningComponent(api_key="GEMINI_API_KEY")

orchestrator = ReasoningOrchestratorV2(
    classifier=classifier,
    llm_component=llm_component,
    semantic_registry=semantic_registry,
    executor=executor
)

# Sử dụng
result = orchestrator.reason_with_verification(request)
```

---

## 8. Notes

- **Không modify bất kỳ file hiện tại nào** - chỉ tạo files mới
- **Giữ backward compatibility** - orchestrator cũ vẫn hoạt động
- **Classifier có thể disable** - fallback về rule-based
- **LLM reasoning là optional** - complex queries bắt buộc cần LLM
- **Tất cả LLM calls dùng Gemini 2.0 Flash**
