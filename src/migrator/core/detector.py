import importlib
import importlib.util
import inspect
import sys
from pathlib import Path
from typing import Any, List, Optional

from migrator.core.constants import COMMON_MODEL_PATHS, EXCLUDED_DIRS


class ModelDetector:
    """Auto-detect SQLAlchemy Base classes"""
    
    searched_paths: List[str] = []

    @classmethod
    def find_base(cls, explicit_path: Optional[str] = None) -> Optional[Any]:
        """Find SQLAlchemy declarative base"""
        cls.searched_paths = []
        
        if explicit_path:
            cls.searched_paths.append(explicit_path)
            base = cls._try_explicit_path(explicit_path)
            if base:
                return base
        
        for path in COMMON_MODEL_PATHS:
            cls.searched_paths.append(path)
            base = cls._try_import(path)
            if base:
                return base

        cls.searched_paths.append("project scan")
        return cls._scan_project()
    
    @classmethod
    def get_searched_paths(cls) -> List[str]:
        """Get list of paths that were searched"""
        return cls.searched_paths
    
    @staticmethod
    def _try_explicit_path(path: str) -> Optional[Any]:
        """Load Base from explicit path like 'app.core.database:Base'"""
        try:
            if ":" in path:
                module_path, attr_name = path.split(":", 1)
            else:
                module_path = path
                attr_name = "Base"
            
            sys.path.insert(0, str(Path.cwd()))
            module = importlib.import_module(module_path)
            
            if hasattr(module, attr_name):
                obj = getattr(module, attr_name)
                if hasattr(obj, "metadata") and hasattr(obj, "registry"):
                    return obj
        except (ImportError, AttributeError, ValueError):
            pass
        
        return None

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
                module_name = py_file.stem
                spec = importlib.util.spec_from_file_location(module_name, py_file)
                if not spec or not spec.loader:
                    continue

                sys.path.insert(0, str(py_file.parent))
                module = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = module
                spec.loader.exec_module(module)

                for name, obj in inspect.getmembers(module):
                    if (
                        name == "Base"
                        and hasattr(obj, "metadata")
                        and hasattr(obj, "registry")
                        and not obj.__module__.startswith("sqlalchemy")
                    ):
                        return obj
            except Exception:
                continue
        return None
