"""Reasoning orchestrator - manages reasoning flow with skill retrieval"""

from typing import List, Dict, Any, Optional
from .chain import ChainOfThought
from .tree import TreeOfThought
from .reflector import SelfReflector
from .verifier import VerificationEngine
from ..types import AnalysisRequest, AnalysisResult, ThoughtStep, ReasoningMode
from ..skills import SkillManager, Skill


class ReasoningOrchestrator:
    """Main orchestrator for reasoning framework with skill retrieval capability"""

    def __init__(self, semantic_registry: Any, executor: Any):
        self.semantic = semantic_registry
        self.executor = executor

        self.cot = ChainOfThought(semantic_registry, executor)
        self.tot = TreeOfThought(self.cot)
        self.reflector = SelfReflector()
        self.verifier = VerificationEngine()

        self.skill_manager = SkillManager()

    def get_skill(self, skill_name: str) -> Optional[Skill]:
        """Get skill by name - for agent to retrieve skill context"""
        return self.skill_manager.get_skill(skill_name)

    def get_skill_content(self, skill_name: str) -> Optional[str]:
        """Get skill content as string for prompt injection"""
        return self.skill_manager.get_skill_content(skill_name)

    def list_skills(self) -> List[str]:
        """List all available skills"""
        return self.skill_manager.list_skills()

    def search_skills(self, query: str) -> List[Skill]:
        """Search skills matching query"""
        return self.skill_manager.search_skills(query)

    def get_skill_for_task(self, task: str) -> Optional[Skill]:
        """Automatically find best matching skill for task"""
        results = self.skill_manager.search_skills(task)
        return results[0] if results else None

    def reason(self, request: AnalysisRequest) -> List[ThoughtStep]:
        """Execute reasoning based on mode"""
        if request.reasoning_mode == ReasoningMode.TREE_OF_THOUGHT:
            return self.tot.reason(request)
        return self.cot.reason(request)

    def reflect(self, steps: List[ThoughtStep]) -> Any:
        """Reflect on reasoning steps"""
        return self.reflector.reflect(steps)

    def verify(self, result: Any, constraints: Dict[str, Any]) -> Any:
        """Verify result against constraints"""
        return self.verifier.verify(result, constraints)

    def execute_with_verification(
        self, request: AnalysisRequest, max_retries: int = 3
    ) -> AnalysisResult:
        """Execute reasoning with verification and retry"""
        attempts = []

        for attempt in range(max_retries):
            steps = self.reason(request)
            reflection = self.reflect(steps)

            if reflection.is_valid or attempt == max_retries - 1:
                return AnalysisResult(
                    answer=f"Analysis completed with {len(steps)} steps",
                    data=steps[-1].result if steps else None,
                    reasoning_trace=steps,
                    confidence=reflection.confidence,
                    errors=reflection.issues if not reflection.is_valid else [],
                )

            attempts.append({"steps": steps, "reflection": reflection})

        return AnalysisResult(
            answer="Analysis failed after maximum retries",
            reasoning_trace=attempts[-1]["steps"] if attempts else [],
            confidence=0.0,
            errors=["Max retries exceeded"],
        )
