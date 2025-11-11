import importlib
import importlib.util
import inspect
import sys
from pathlib import Path
from typing import Any, Optional

from migrator.core.constants import COMMON_MODEL_PATHS, EXCLUDED_DIRS


class ModelDetector:
    """Auto-detect SQLAlchemy Base classes"""

    @classmethod
    def find_base(cls) -> Optional[Any]:
        """Find SQLAlchemy declarative base"""
        for path in COMMON_MODEL_PATHS:
            base = cls._try_import(path)
            if base:
                return base

        return cls._scan_project()

    @staticmethod
    def _try_import(module_path: str) -> Optional[Any]:
        try:
            sys.path.insert(0, str(Path.cwd()))
            module = importlib.import_module(module_path)

            if hasattr(module, "Base"):
                return module.Base

            for name, obj in inspect.getmembers(module):
                if hasattr(obj, "metadata") and hasattr(obj, "registry"):
                    return obj
        except (ImportError, AttributeError):
            pass
        return None

    @staticmethod
    def _scan_project() -> Optional[Any]:
        """Scan .py files for Base classes"""
        for py_file in Path.cwd().rglob("*.py"):
            if any(excluded in str(py_file) for excluded in EXCLUDED_DIRS):
                continue

            try:
                spec = importlib.util.spec_from_file_location("temp_module", py_file)
                if not spec or not spec.loader:
                    continue

                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                for name, obj in inspect.getmembers(module):
                    if hasattr(obj, "metadata") and hasattr(obj, "registry"):
                        return obj
            except Exception:
                continue
        return None
