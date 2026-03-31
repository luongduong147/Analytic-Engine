"""Code execution in secure sandbox"""

import subprocess
import tempfile
import time
import json
from pathlib import Path
from typing import Optional, Callable, Dict, Any
from ..types import ExecutionConfig, ExecutionResult


class CodeExecutor:
    """Secure Python code execution in isolated environment"""

    DANGEROUS_IMPORTS = [
        "os",
        "sys",
        "subprocess",
        "socket",
        "requests",
        "urllib",
        "http",
        "ftplib",
        "smtplib",
        "pty",
        "importlib",
        "builtins",
        "exec",
        "eval",
        "compile",
    ]

    def __init__(self, config: Optional[ExecutionConfig] = None):
        self.config = config or ExecutionConfig()

    def validate_code(self, code: str) -> tuple[bool, Optional[str]]:
        """Check for dangerous operations before execution"""
        lines = code.split("\n")
        for line in lines:
            for dangerous in self.DANGEROUS_IMPORTS:
                if f"import {dangerous}" in line or f"from {dangerous} " in line:
                    return False, f"Import '{dangerous}' is not allowed"

            if any(x in line for x in ["eval(", "exec(", "compile("]):
                return False, "Dynamic code execution is not allowed"

        return True, None

    def execute(self, code: str, context: Optional[Dict[str, Any]] = None) -> ExecutionResult:
        """Execute Python code in sandbox"""
        start_time = time.time()

        is_valid, error = self.validate_code(code)
        if not is_valid:
            return ExecutionResult(
                success=False, output=None, error=error, execution_time=time.time() - start_time
            )

        context_code = ""
        if context:
            context_code = "\n".join([f"{k} = {repr(v)}" for k, v in context.items()])
            code = f"{context_code}\n{code}"

        try:
            result = self._execute_isolated(code)
            return ExecutionResult(
                success=True, output=result, execution_time=time.time() - start_time
            )
        except Exception as e:
            return ExecutionResult(
                success=False, output=None, error=str(e), execution_time=time.time() - start_time
            )

    def _execute_isolated(self, code: str) -> Any:
        """Execute in subprocess with limits"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            temp_path = f.name

        try:
            result = subprocess.run(
                ["python", temp_path],
                capture_output=True,
                text=True,
                timeout=self.config.timeout,
                cwd=tempfile.gettempdir(),
            )

            if result.returncode != 0:
                raise Exception(result.stderr)

            if result.stdout.strip():
                try:
                    return json.loads(result.stdout)
                except json.JSONDecodeError:
                    return result.stdout.strip()

            return None

        finally:
            Path(temp_path).unlink(missing_ok=True)
