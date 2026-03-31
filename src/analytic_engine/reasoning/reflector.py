"""Self-reflection for reasoning framework"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from ..types import ThoughtStep, ReflectionResult


class SelfReflector:
    """Self-reflection capabilities for reasoning"""

    def __init__(self, min_confidence_threshold: float = 0.5):
        self.min_confidence = min_confidence_threshold

    def reflect(self, steps: List[ThoughtStep]) -> ReflectionResult:
        """Reflect on reasoning steps"""
        issues: List[str] = []
        suggestions: List[str] = []

        if not steps:
            return ReflectionResult(
                is_valid=False,
                confidence=0.0,
                issues=["No reasoning steps to reflect on"],
                suggested_fix="Start with a valid analysis request",
            )

        low_confidence_steps = [s for s in steps if s.confidence < self.min_confidence]
        if low_confidence_steps:
            issues.append(f"{len(low_confidence_steps)} steps have low confidence")
            suggestions.append("Review and retry low-confidence steps")

        failed_steps = [s for s in steps if s.result is None and s.action != "start"]
        if failed_steps:
            issues.append(f"{len(failed_steps)} steps produced no result")
            suggestions.append("Check data availability and action parameters")

        avg_confidence = sum(s.confidence for s in steps) / len(steps)

        should_retry = len(issues) > 0 and avg_confidence < 0.7

        return ReflectionResult(
            is_valid=avg_confidence >= self.min_confidence,
            confidence=avg_confidence,
            issues=issues,
            suggested_fix=suggestions[0] if suggestions else None,
        )

    def analyze_errors(self, steps: List[ThoughtStep]) -> Dict[str, Any]:
        """Analyze errors in reasoning steps"""
        error_patterns: Dict[str, int] = {}

        for step in steps:
            if step.result is None and step.action != "start":
                error_patterns["failed_actions"] = error_patterns.get("failed_actions", 0) + 1

            if step.confidence < 0.5:
                error_patterns["low_confidence"] = error_patterns.get("low_confidence", 0) + 1

        return {
            "total_steps": len(steps),
            "error_patterns": error_patterns,
            "overall_health": 1.0 - (sum(error_patterns.values()) / max(len(steps), 1)),
        }

    def suggest_improvements(self, steps: List[ThoughtStep]) -> List[str]:
        """Suggest improvements based on reflection"""
        suggestions = []

        reflection = self.reflect(steps)

        if reflection.confidence < 0.8:
            suggestions.append("Consider using more granular reasoning steps")

        if len(steps) > 5:
            suggestions.append("Try breaking down complex objectives into simpler sub-tasks")

        action_counts: Dict[str, int] = {}
        for step in steps:
            action_counts[step.action] = action_counts.get(step.action, 0) + 1

        if len(action_counts) == 1:
            suggestions.append("Try different action types for varied perspectives")

        return suggestions
