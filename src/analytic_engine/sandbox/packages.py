"""Allowed packages configuration"""

from typing import List, Set

DEFAULT_PACKAGES: List[str] = [
    "pandas",
    "numpy",
    "scipy",
    "statsmodels",
    "sklearn",
    "prophet",
    "matplotlib",
    "plotly",
    "seaborn",
    "json",
    "datetime",
    "math",
    "re",
]

PACKAGE_ALIASES: dict = {
    "np": "numpy",
    "pd": "pandas",
    "plt": "matplotlib",
    "sns": "seaborn",
    "sklearn": "scikit-learn",
}


class PackageManager:
    """Manages allowed packages for sandbox execution"""

    def __init__(self, packages: List[str] = None):
        self._allowed_packages: Set[str] = set(packages or DEFAULT_PACKAGES)
        self._build_import_map()

    def _build_import_map(self) -> None:
        self._import_map = {}
        for pkg in self._allowed_packages:
            self._import_map[pkg] = pkg
        for alias, original in PACKAGE_ALIASES.items():
            if original in self._allowed_packages:
                self._import_map[alias] = original

    def is_allowed(self, package_name: str) -> bool:
        normalized = self._import_map.get(package_name, package_name)
        return normalized in self._allowed_packages

    def get_allowed_imports(self) -> str:
        imports = []
        for pkg in sorted(self._allowed_packages):
            if pkg == "sklearn":
                imports.append("from sklearn import *")
            elif pkg in PACKAGE_ALIASES.values():
                imports.append(f"import {pkg}")
        return "\n".join(imports)

    def add_package(self, package: str) -> None:
        self._allowed_packages.add(package)
        self._build_import_map()

    def remove_package(self, package: str) -> None:
        self._allowed_packages.discard(package)
        self._build_import_map()

    @property
    def allowed_packages(self) -> List[str]:
        return sorted(list(self._allowed_packages))
