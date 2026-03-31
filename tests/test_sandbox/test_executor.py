"""Tests for sandbox code execution"""

import pytest
import json
from analytic_engine.sandbox.executor import CodeExecutor
from analytic_engine.types import ExecutionConfig, ExecutionResult


class TestCodeExecutor:
    """Test cases for CodeExecutor"""

    def test_execute_simple_code(self, code_executor):
        """Test execution of simple valid code"""
        code = "print(json.dumps({'result': 42}))"
        result = code_executor.execute(code)

        assert result.success is True
        assert result.output is not None

    def test_execute_with_context(self, code_executor):
        """Test code execution with context variables"""
        code = "print(json.dumps({'sum': a + b}))"
        context = {"a": 10, "b": 20}
        result = code_executor.execute(code, context=context)

        assert result.success is True

    def test_validate_code_dangerous_import(self, code_executor):
        """Test detection of dangerous import statements"""
        code = "import os\nprint('hello')"
        is_valid, error = code_executor.validate_code(code)

        assert is_valid is False
        assert "os" in error

    def test_validate_code_dangerous_from_import(self, code_executor):
        """Test detection of dangerous from imports"""
        code = "from subprocess import Popen\nprint('hello')"
        is_valid, error = code_executor.validate_code(code)

        assert is_valid is False
        assert "subprocess" in error

    def test_validate_code_eval(self, code_executor):
        """Test detection of eval() usage"""
        code = "result = eval('2 + 2')"
        is_valid, error = code_executor.validate_code(code)

        assert is_valid is False
        assert "eval" in error.lower()

    def test_validate_code_exec(self, code_executor):
        """Test detection of exec() usage"""
        code = "exec('print(1)')"
        is_valid, error = code_executor.validate_code(code)

        assert is_valid is False
        assert "exec" in error.lower()

    def test_validate_code_compile(self, code_executor):
        """Test detection of compile() usage"""
        code = "compile('1', 'test', 'eval')"
        is_valid, error = code_executor.validate_code(code)

        assert is_valid is False
        assert "compile" in error.lower()

    def test_validate_code_safe(self, code_executor):
        """Test validation passes for safe code"""
        code = "import pandas as pd\ndf = pd.DataFrame()"
        is_valid, error = code_executor.validate_code(code)

        assert is_valid is True
        assert error is None

    def test_execute_blocked_import_returns_error(self, code_executor):
        """Test execution fails with blocked import"""
        code = "import socket\nprint('hello')"
        result = code_executor.execute(code)

        assert result.success is False
        assert result.error is not None

    def test_execute_syntax_error_returns_error(self, code_executor):
        """Test execution handles syntax errors"""
        code = "print('unclosed"
        result = code_executor.execute(code)

        assert result.success is False
        assert result.error is not None

    def test_execution_time_recorded(self, code_executor):
        """Test that execution time is recorded"""
        code = "print(json.dumps({'ok': True}))"
        result = code_executor.execute(code)

        assert result.execution_time > 0

    def test_default_allowed_packages(self, execution_config):
        """Test default allowed packages include common data science packages"""
        assert "pandas" in execution_config.allowed_packages
        assert "numpy" in execution_config.allowed_packages
        assert "matplotlib" in execution_config.allowed_packages


class TestExecutionConfig:
    """Test cases for ExecutionConfig"""

    def test_default_timeout(self):
        """Test default timeout is 30 seconds"""
        config = ExecutionConfig()
        assert config.timeout == 30

    def test_default_memory_limit(self):
        """Test default memory limit is 512 MB"""
        config = ExecutionConfig()
        assert config.memory_limit == 512

    def test_custom_timeout(self):
        """Test custom timeout configuration"""
        config = ExecutionConfig(timeout=60)
        assert config.timeout == 60

    def test_custom_allowed_packages(self):
        """Test custom allowed packages"""
        packages = ["pandas", "numpy"]
        config = ExecutionConfig(allowed_packages=packages)
        assert config.allowed_packages == packages


class TestExecutionResult:
    """Test cases for ExecutionResult"""

    def test_successful_result(self):
        """Test successful execution result"""
        result = ExecutionResult(success=True, output={"data": 123})

        assert result.success is True
        assert result.output == {"data": 123}
        assert result.error is None

    def test_failed_result(self):
        """Test failed execution result"""
        result = ExecutionResult(success=False, error="Import blocked")

        assert result.success is False
        assert result.error == "Import blocked"
        assert result.output is None
