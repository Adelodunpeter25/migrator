from pathlib import Path

import pytest

from migrator.core.alembic_backend import AlembicBackend
from migrator.core.config import MigratorConfig


@pytest.fixture
def test_config():
    """Create test configuration"""
    return MigratorConfig(
        database_url="sqlite:///test.db",
        migrations_dir=Path("migrations"),
        base_import_path="models.Base",
    )


def test_alembic_backend_init(test_config, temp_dir):
    """Test AlembicBackend initialization"""
    backend = AlembicBackend(test_config)
    assert backend.config == test_config
    assert backend.alembic_cfg is not None


def test_init_creates_migration_directory(test_config, temp_dir):
    """Test that init creates migration directory structure"""
    backend = AlembicBackend(test_config)
    migrations_dir = temp_dir / "migrations"

    backend.init(migrations_dir)

    assert migrations_dir.exists()
    assert (migrations_dir / "versions").exists()
    assert (migrations_dir / "env.py").exists()
    assert (migrations_dir / "script.py.mako").exists()
    assert (migrations_dir / "alembic.ini").exists()


def test_env_py_contains_base_import(test_config, temp_dir):
    """Test that env.py contains the Base import"""
    backend = AlembicBackend(test_config)
    migrations_dir = temp_dir / "migrations"

    backend.init(migrations_dir)

    env_content = (migrations_dir / "env.py").read_text()
    assert "from models import Base" in env_content
    assert "Base.metadata" in env_content
