"""Semantic action registry"""

from typing import Dict, Callable, Any


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
