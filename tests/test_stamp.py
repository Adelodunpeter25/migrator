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


def test_stamp_command_exists(test_config):
    """Test that stamp method exists"""
    backend = AlembicBackend(test_config)
    assert hasattr(backend, "stamp")


def test_check_existing_tables(test_config):
    """Test checking for existing tables"""
    backend = AlembicBackend(test_config)
    tables = backend.check_existing_tables()
    assert isinstance(tables, list)


def test_get_pending_migrations(test_config, temp_dir):
    """Test getting pending migrations"""
    backend = AlembicBackend(test_config)
    migrations_dir = temp_dir / "migrations"
    backend.init(migrations_dir)

    pending = backend.get_pending_migrations()
    assert isinstance(pending, list)
