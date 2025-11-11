from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional


class MigrationBackend(ABC):
    """Abstract interface for migration backends"""

    @abstractmethod
    def init(self, directory: Path) -> None:
        """Initialize migration environment"""
        pass

    @abstractmethod
    def create_migration(self, message: str, autogenerate: bool = True) -> Path:
        """Create new migration"""
        pass

    @abstractmethod
    def apply_migrations(self, revision: str = "head") -> None:
        """Apply migrations"""
        pass

    @abstractmethod
    def downgrade(self, revision: str = "-1") -> None:
        """Rollback migrations"""
        pass

    @abstractmethod
    def history(self) -> List[dict]:
        """Get migration history"""
        pass

    @abstractmethod
    def current(self) -> Optional[str]:
        """Get current revision"""
        pass
