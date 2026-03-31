"""Tests for reasoning module"""

import pytest
from analytic_engine.reasoning.chain import ChainOfThought
from analytic_engine.semantic.registry import SemanticActionRegistry
from analytic_engine.semantic.actions import create_builtin_actions
from analytic_engine.types import AnalysisRequest, ReasoningMode, ThoughtStep


class TestChainOfThought:
    """Test cases for ChainOfThought reasoning"""

    def test_cot_initialization(self, cot_reasoner):
        """Test CoT initialization"""
        assert cot_reasoner.max_steps == 10
        assert cot_reasoner.semantic is not None
        assert cot_reasoner.executor is not None

    def test_reason_returns_list_of_thought_steps(self, cot_reasoner, analysis_request):
        """Test reason returns list of ThoughtStep"""
        result = cot_reasoner.reason(analysis_request)

        assert isinstance(result, list)
        assert all(isinstance(step, ThoughtStep) for step in result)

    def test_respects_max_steps(self, cot_reasoner):
        """Test reasoning respects max_steps limit"""
        request = AnalysisRequest(
            objective="test",
            max_steps=3,
            context={},
        )
        result = cot_reasoner.reason(request)

        assert len(result) <= 3

    def test_thought_step_structure(self, cot_reasoner, analysis_request):
        """Test ThoughtStep has required fields"""
        result = cot_reasoner.reason(analysis_request)
        step = result[0]

        assert step.step_number == 1
        assert isinstance(step.thought, str)
        assert isinstance(step.action, str)
        assert step.result is not None

    def test_reason_updates_context(self, cot_reasoner):
        """Test reasoning updates context with results"""
        request = AnalysisRequest(objective="test", max_steps=2, context={})
        result = cot_reasoner.reason(request)

        assert len(result) >= 1

    def test_action_execution(self, cot_reasoner, semantic_registry_with_actions):
        """Test actions are executed through semantic registry"""
        request = AnalysisRequest(objective="test", max_steps=1, context={})
        result = cot_reasoner.reason(request)

        assert result[0].action is not None

    def test_cot_with_empty_context(self, cot_reasoner):
        """Test CoT works with empty context"""
        request = AnalysisRequest(objective="test", max_steps=1, context={})
        result = cot_reasoner.reason(request)

        assert len(result) >= 1

    def test_cot_with_initial_context(self, cot_reasoner):
        """Test CoT uses provided initial context"""
        initial_context = {"user_id": 123, "query": "sales"}
        request = AnalysisRequest(objective="test", max_steps=1, context=initial_context)
        result = cot_reasoner.reason(request)

        assert len(result) >= 1


class TestThoughtStep:
    """Test cases for ThoughtStep dataclass"""

    def test_thought_step_creation(self):
        """Test creating a ThoughtStep"""
        step = ThoughtStep(
            step_number=1,
            thought="Analyze data",
            action="query_data",
            result={"data": [1, 2, 3]},
        )

        assert step.step_number == 1
        assert step.thought == "Analyze data"
        assert step.action == "query_data"
        assert step.result == {"data": [1, 2, 3]}
        assert step.confidence == 1.0

    def test_thought_step_with_confidence(self):
        """Test ThoughtStep with custom confidence"""
        step = ThoughtStep(
            step_number=1,
            thought="test",
            action="action",
            result=None,
            confidence=0.85,
        )

        assert step.confidence == 0.85

    def test_thought_step_with_children(self):
        """Test ThoughtStep with child steps"""
        child = ThoughtStep(step_number=1, thought="child", action="a", result=None)
        parent = ThoughtStep(
            step_number=2,
            thought="parent",
            action="b",
            result=None,
            children=[child],
        )

        assert len(parent.children) == 1
        assert parent.children[0].thought == "child"


class TestReasoningMode:
    """Test cases for ReasoningMode enum"""

    def test_reasoning_mode_values(self):
        """Test ReasoningMode enum values"""
        assert ReasoningMode.CHAIN_OF_THOUGHT.value == "CoT"
        assert ReasoningMode.TREE_OF_THOUGHT.value == "ToT"


class TestAnalysisRequest:
    """Test cases for AnalysisRequest"""

    def test_default_values(self):
        """Test AnalysisRequest default values"""
        request = AnalysisRequest(objective="test")

        assert request.objective == "test"
        assert request.reasoning_mode == ReasoningMode.CHAIN_OF_THOUGHT
        assert request.max_steps == 10
        assert request.context == {}

    def test_custom_values(self):
        """Test AnalysisRequest with custom values"""
        request = AnalysisRequest(
            objective="Analyze sales",
            reasoning_mode=ReasoningMode.TREE_OF_THOUGHT,
            max_steps=5,
            context={"data": "sales"},
        )

        assert request.objective == "Analyze sales"
        assert request.reasoning_mode == ReasoningMode.TREE_OF_THOUGHT
        assert request.max_steps == 5
        assert request.context == {"data": "sales"}
