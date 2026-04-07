from .test_sandbox.test_executor import TestCodeExecutor

class TestLinhtinh(TestCodeExecutor):
    """Test cases for Linhtinh agent"""

    def __init__ (self):
        super().__init__()
    
    def test_linhtinh_basic_execution(self, code_executor):
        """Test basic code execution in Linhtinh agent"""
        code = "print('Hello, Linhtinh!')"
        result = code_executor.execute(code)

        assert result.success is True
        assert result.output is not None

    def test_linhtinh_execution_with_context(self, code_executor):
        """Test code execution with context in Linhtinh agent"""
        code = "print(f'Context value: {context_value}')"
        context = {"context_value": "Test Context"}
        result = code_executor.execute(code, context=context)

        assert result.success is True
        assert result.output is not None

if __name__ == "__main__":
    test_agent = TestLinhtinh()
    test_agent.test_linhtinh_basic_execution()
    test_agent.test_linhtinh_execution_with_context()