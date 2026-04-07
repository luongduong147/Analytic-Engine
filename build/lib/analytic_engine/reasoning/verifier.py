"""Result verification for reasoning framework"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from ..types import ThoughtStep, VerificationResult


class VerificationEngine:
    """Verify reasoning results against constraints"""

    def __init__(self, strict_mode: bool = False):
        self.strict_mode = strict_mode

    def verify(self, result: Any, constraints: Dict[str, Any]) -> VerificationResult:
        """Verify result against constraints"""
        errors: List[str] = []
        warnings: List[str] = []

        if "expected_type" in constraints:
            expected = constraints["expected_type"]
            if not self._check_type(result, expected):
                errors.append(
                    f"Result type mismatch: expected {expected}, got {type(result).__name__}"
                )

        if "min_value" in constraints:
            if isinstance(result, (int, float)):
                if result < constraints["min_value"]:
                    errors.append(f"Value {result} below minimum {constraints['min_value']}")

        if "max_value" in constraints:
            if isinstance(result, (int, float)):
                if result > constraints["max_value"]:
                    errors.append(f"Value {result} above maximum {constraints['max_value']}")

        if "allowed_values" in constraints:
            if result not in constraints["allowed_values"]:
                errors.append(
                    f"Value {result} not in allowed values: {constraints['allowed_values']}"
                )

        if "max_length" in constraints:
            if hasattr(result, "__len__") and len(result) > constraints["max_length"]:
                errors.append(
                    f"Result length {len(result)} exceeds max {constraints['max_length']}"
                )

        if self.strict_mode and warnings:
            errors.extend(warnings)
            warnings.clear()

        return VerificationResult(valid=len(errors) == 0, errors=errors, warnings=warnings)

    def _check_type(self, result: Any, expected: str) -> bool:
        """Check if result matches expected type"""
        type_map = {
            "DataFrame": "DataFrame",
            "dict": "dict",
            "list": "list",
            "int": "int",
            "float": "float",
            "str": "str",
        }
        return type(result).__name__ == type_map.get(expected, expected)

    def verify_reasoning_steps(self, steps: List[ThoughtStep]) -> VerificationResult:
        """Verify reasoning steps are coherent"""
        errors: List[str] = []
        warnings: List[str] = []

        if not steps:
            errors.append("No reasoning steps to verify")
            return VerificationResult(valid=False, errors=errors)

        if steps[0].action == "start" and steps[0].result is not None:
            warnings.append("Start step should not have result")

        for i, step in enumerate(steps):
            if step.step_number != i + 1:
                errors.append(f"Step number mismatch at index {i}")

            if step.confidence < 0 and step.action != "start":
                errors.append(f"Negative confidence at step {i + 1}")

        return VerificationResult(valid=len(errors) == 0, errors=errors, warnings=warnings)

    def verify_data_constraints(self, data: Any, constraints: Dict[str, Any]) -> VerificationResult:
        """Verify data meets constraints"""
        errors: List[str] = []
        warnings: List[str] = []

        if "not_empty" in constraints and constraints["not_empty"]:
            if data is None or (hasattr(data, "__len__") and len(data) == 0):
                errors.append("Data is empty")

        if "min_rows" in constraints:
            if hasattr(data, "__len__") and data.shape[0] < constraints["min_rows"]:
                errors.append(f"Row count {data.shape[0]} below minimum {constraints['min_rows']}")

        if "required_columns" in constraints:
            if hasattr(data, "columns"):
                missing = set(constraints["required_columns"]) - set(data.columns)
                if missing:
                    errors.append(f"Missing required columns: {missing}")

        return VerificationResult(valid=len(errors) == 0, errors=errors, warnings=warnings)
