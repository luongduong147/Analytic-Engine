"""Main agent class for Analytic Engine"""

from typing import Dict, Any, List, Optional, Callable
from .config import Config
from .types import (
    AnalysisRequest,
    AnalysisResult,
    ExecutionConfig,
    ReasoningMode,
    ChartType,
    ExecutionResult as ExecResult,
    ThoughtStep,
)
from .sandbox.executor import CodeExecutor
from .semantic.registry import SemanticActionRegistry
from .semantic.actions import create_builtin_actions
from .reasoning.orchestrator import ReasoningOrchestrator
from .visualization.engine import VisualizationEngine


class AnalyticEngineAgent:
    """Main entry point for the analytic engine"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = Config(config if config is not None else {})

        self.sandbox = CodeExecutor(self.config.execution)
        self.semantic = SemanticActionRegistry()
        self.viz = VisualizationEngine()

        self._register_actions()
        self.reasoning = ReasoningOrchestrator(self.semantic, self.sandbox.execute)

    def _register_actions(self) -> None:
        """Register built-in semantic actions"""
        actions = create_builtin_actions()
        for name, handler in actions.items():
            self.semantic.register(name, handler)

    def analyze(self, request: AnalysisRequest) -> AnalysisResult:
        """Execute complete analysis request"""
        try:
            reasoning_trace = self.reasoning.reason(request)
            reflection = self.reasoning.reflect(reasoning_trace)

            answer = self._extract_answer(reasoning_trace)

            return AnalysisResult(
                answer=answer,
                data=reasoning_trace[-1].result if reasoning_trace else None,
                reasoning_trace=reasoning_trace,
                confidence=reflection.confidence if reflection else 1.0,
                errors=reflection.issues if reflection and not reflection.is_valid else [],
            )

        except Exception as e:
            return AnalysisResult(answer="", errors=[str(e)], confidence=0.0)

    def execute_code(self, code: str, context: Optional[Dict[str, Any]] = None) -> ExecResult:
        """Execute Python code in sandbox"""
        return self.sandbox.execute(code, context if context is not None else {})

    def fetch_data(self, action: str, params: Dict[str, Any]) -> Any:
        """Fetch data via semantic actions"""
        return self.semantic.execute(action, params)

    def visualize(self, data: Any, chart_type: str, config: Optional[Dict[str, Any]] = None) -> Any:
        """Generate visualization"""
        return self.viz.generate(data, ChartType(chart_type), config or {})

    def register_semantic_action(self, name: str, handler: Callable) -> None:
        """Register custom semantic action"""
        self.semantic.register(name, handler)

    def _extract_answer(self, reasoning_trace: List[ThoughtStep]) -> str:
        """Extract final answer from reasoning trace"""
        if not reasoning_trace:
            return "No reasoning steps completed"
        return f"Analysis completed with {len(reasoning_trace)} steps"
