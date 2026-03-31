"""Configuration management"""

from typing import Dict, Any
from .types import ExecutionConfig


class Config:
    """Configuration management for the analytic engine"""

    def __init__(self, custom: Dict[str, Any] = None):
        self.execution = ExecutionConfig()
        self._custom: Dict[str, Any] = custom if custom is not None else {}

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self._custom.get(key, default)

    def set_execution_limit(self, timeout: int = None, memory: int = None) -> None:
        """Set execution limits"""
        if timeout is not None:
            self.execution.timeout = timeout
        if memory is not None:
            self.execution.memory_limit = memory

    @property
    def default_packages(self) -> list:
        """Get default allowed packages"""
        return self.execution.allowed_packages
