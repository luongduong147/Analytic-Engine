"""Security validation for sandbox execution"""

import re
from typing import List, Tuple


class SecurityValidator:
    """Validates code for security concerns"""

    DANGEROUS_PATTERNS = [
        (r"import\s+os\b", "Module 'os' is not allowed"),
        (r"import\s+sys\b", "Module 'sys' is not allowed"),
        (r"import\s+subprocess\b", "Module 'subprocess' is not allowed"),
        (r"import\s+socket\b", "Module 'socket' is not allowed"),
        (r"import\s+requests\b", "Module 'requests' is not allowed"),
        (r"import\s+urllib\b", "Module 'urllib' is not allowed"),
        (r"import\s+http\b", "Module 'http' is not allowed"),
        (r"import\s+ftplib\b", "Module 'ftplib' is not allowed"),
        (r"import\s+smtplib\b", "Module 'smtplib' is not allowed"),
        (r"import\s+pty\b", "Module 'pty' is not allowed"),
        (r"import\s+importlib\b", "Module 'importlib' is not allowed"),
        (r"import\s+builtins\b", "Module 'builtins' is not allowed"),
        (r"from\s+os\s+import", "Module 'os' is not allowed"),
        (r"from\s+sys\s+import", "Module 'sys' is not allowed"),
        (r"from\s+subprocess\s+import", "Module 'subprocess' is not allowed"),
        (r"from\s+socket\s+import", "Module 'socket' is not allowed"),
        (r"from\s+requests\s+import", "Module 'requests' is not allowed"),
        (r"\beval\s*\(", "eval() is not allowed"),
        (r"\bexec\s*\(", "exec() is not allowed"),
        (r"\bcompile\s*\(", "compile() is not allowed"),
        (r"__import__\s*\(", "__import__() is not allowed"),
        (r"import\s+\.", "Relative imports are not allowed"),
        (r"import\s+\w+\.\.", "Nested imports are not allowed"),
    ]

    FILE_ACCESS_PATTERNS = [
        (r"open\s*\([^)]*['\"][wr][a-z]*['\"]", "File write operations are not allowed"),
        (r"\bwrite\s*\(", "File write operations are not allowed"),
        (r"\bmkdir\s*\(", "Directory creation is not allowed"),
        (r"\brmdir\s*\(", "Directory removal is not allowed"),
        (r"\bremove\s*\(", "File removal is not allowed"),
        (r"\bunlink\s*\(", "File removal is not allowed"),
    ]

    NETWORK_PATTERNS = [
        (r"socket\s*\.\s*connect", "Network connections are not allowed"),
        (r"urllib\.request", "Network requests are not allowed"),
        (r"requests\.get", "Network requests are not allowed"),
        (r"requests\.post", "Network requests are not allowed"),
        (r"ftplib", "FTP connections are not allowed"),
        (r"smtplib", "Email sending is not allowed"),
    ]

    def __init__(self):
        self._compiled_dangerous = [
            (re.compile(pattern), message) for pattern, message in self.DANGEROUS_PATTERNS
        ]
        self._compiled_file = [
            (re.compile(pattern), message) for pattern, message in self.FILE_ACCESS_PATTERNS
        ]
        self._compiled_network = [
            (re.compile(pattern), message) for pattern, message in self.NETWORK_PATTERNS
        ]

    def validate(self, code: str) -> Tuple[bool, List[str]]:
        """
        Validate code for security issues

        Returns:
            Tuple of (is_valid, list of errors)
        """
        errors = []

        errors.extend(self._check_patterns(code, self._compiled_dangerous))
        errors.extend(self._check_patterns(code, self._compiled_file))
        errors.extend(self._check_patterns(code, self._compiled_network))

        return len(errors) == 0, errors

    def _check_patterns(self, code: str, patterns: List) -> List[str]:
        errors = []
        for compiled, message in patterns:
            if compiled.search(code):
                errors.append(message)
        return errors

    def is_code_safe(self, code: str) -> bool:
        """Quick check if code is safe"""
        is_valid, _ = self.validate(code)
        return is_valid


class SandboxSecurity:
    """Security configuration for sandbox"""

    ALLOWED_BUILTINS = [
        "print",
        "len",
        "str",
        "int",
        "float",
        "bool",
        "list",
        "dict",
        "tuple",
        "set",
        "range",
        "enumerate",
        "zip",
        "map",
        "filter",
        "sum",
        "min",
        "max",
        "abs",
        "round",
        "sorted",
        "reversed",
        "type",
        "isinstance",
        "hasattr",
        "getattr",
        "input",
    ]

    BLOCKED_ATTRIBUTES = [
        "__import__",
        "__builtins__",
        "__class__",
        "__dict__",
        "__module__",
    ]

    def __init__(self):
        self.validator = SecurityValidator()

    def get_restricted_globals(self) -> dict:
        """Get restricted globals for exec"""
        return {"__builtins__": {k: None for k in self.ALLOWED_BUILTINS}}

    def validate_and_get_errors(self, code: str) -> Tuple[bool, List[str]]:
        return self.validator.validate(code)
