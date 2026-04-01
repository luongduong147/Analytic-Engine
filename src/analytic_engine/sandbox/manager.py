"""Sandbox manager for isolated execution environments"""

import subprocess
import threading
import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, Optional, Any, List, Callable
from pathlib import Path

from .executor import CodeExecutor
from .security import SandboxSecurity
from .packages import PackageManager
from ..types import ExecutionConfig, ExecutionResult


@dataclass
class SandboxSession:
    """Represents a sandbox execution session"""

    session_id: str
    created_at: float = field(default_factory=time.time)
    execution_count: int = 0
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SandboxStats:
    """Statistics for sandbox execution"""

    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    total_execution_time: float = 0.0
    active_sessions: int = 0


class SandboxManager:
    """Manages sandbox execution environments"""

    def __init__(self, config: Optional[ExecutionConfig] = None, max_concurrent: int = 5):
        self.config = config or ExecutionConfig()
        self.max_concurrent = max_concurrent

        self.executor = CodeExecutor(self.config)
        self.security = SandboxSecurity()
        self.package_manager = PackageManager(self.config.allowed_packages)

        self._sessions: Dict[str, SandboxSession] = {}
        self._stats = SandboxStats()
        self._lock = threading.Lock()
        self._semaphore = threading.Semaphore(max_concurrent)

    def create_session(self, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Create a new sandbox session"""
        session_id = str(uuid.uuid4())
        session = SandboxSession(session_id=session_id, metadata=metadata or {})
        with self._lock:
            self._sessions[session_id] = session
            self._stats.active_sessions += 1
        return session_id

    def get_session(self, session_id: str) -> Optional[SandboxSession]:
        """Get session by ID"""
        return self._sessions.get(session_id)

    def execute(
        self,
        code: str,
        context: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> ExecutionResult:
        """
        Execute code in sandbox

        Args:
            code: Python code to execute
            context: Variables to inject
            session_id: Optional session ID
            timeout: Optional timeout override

        Returns:
            ExecutionResult
        """
        with self._semaphore:
            start_time = time.time()

            if timeout:
                original_timeout = self.config.timeout
                self.config.timeout = timeout

            try:
                is_valid, errors = self.security.validator.validate(code)
                if not is_valid:
                    return ExecutionResult(
                        success=False,
                        output=None,
                        error=f"Security validation failed: {', '.join(errors)}",
                        execution_time=time.time() - start_time,
                    )

                result = self.executor.execute(code, context)

                with self._lock:
                    self._stats.total_executions += 1
                    if result.success:
                        self._stats.successful_executions += 1
                    else:
                        self._stats.failed_executions += 1
                    self._stats.total_execution_time += result.execution_time

                    if session_id and session_id in self._sessions:
                        self._sessions[session_id].execution_count += 1

                return result

            finally:
                if timeout:
                    self.config.timeout = original_timeout

    def execute_with_session(
        self,
        code: str,
        context: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> tuple[str, ExecutionResult]:
        """Execute code with a new session"""
        session_id = self.create_session(metadata)
        result = self.execute(code, context, session_id)
        return session_id, result

    def close_session(self, session_id: str) -> bool:
        """Close a session"""
        with self._lock:
            if session_id in self._sessions:
                self._sessions[session_id].is_active = False
                self._stats.active_sessions -= 1
                return True
            return False

    def get_stats(self) -> SandboxStats:
        """Get sandbox statistics"""
        with self._lock:
            return SandboxStats(
                total_executions=self._stats.total_executions,
                successful_executions=self._stats.successful_executions,
                failed_executions=self._stats.failed_executions,
                total_execution_time=self._stats.total_execution_time,
                active_sessions=self._stats.active_sessions,
            )

    def list_sessions(self) -> List[SandboxSession]:
        """List all active sessions"""
        with self._lock:
            return [s for s in self._sessions.values() if s.is_active]

    def cleanup_stale_sessions(self, max_age_seconds: float = 3600) -> int:
        """Clean up sessions older than max_age_seconds"""
        current_time = time.time()
        cleaned = 0

        with self._lock:
            session_ids = list(self._sessions.keys())
            for session_id in session_ids:
                session = self._sessions[session_id]
                if current_time - session.created_at > max_age_seconds:
                    session.is_active = False
                    cleaned += 1
                    self._stats.active_sessions -= 1

        return cleaned
