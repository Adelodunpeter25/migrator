from pathlib import Path

import pytest
from sqlalchemy import create_engine, inspect
from typer.testing import CliRunner

from migrator.cli import app

runner = CliRunner()


@pytest.fixture
def setup_test_project(temp_dir, monkeypatch):
    """Setup a test project with models"""
    db_path = temp_dir / "test.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")

    models_file = temp_dir / "models.py"
    models_file.write_text(
        """
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    email = Column(String(100))
"""
    )

    yield temp_dir, db_path


def test_full_migration_workflow(setup_test_project):
    """Test complete migration workflow: init -> makemigrations -> migrate -> downgrade"""
    temp_dir, db_path = setup_test_project
    env = {"DATABASE_URL": f"sqlite:///{db_path}"}

    # Step 1: Initialize migrations
    result = runner.invoke(app, ["init"], env=env)
    assert result.exit_code == 0, f"Init failed: {result.stdout}"
    assert Path("migrations").exists()
    assert Path("migrations/versions").exists()
    assert Path("migrations/env.py").exists()
    assert Path("migrations/script.py.mako").exists()
    assert Path("migrations/alembic.ini").exists()

    env_content = Path("migrations/env.py").read_text()
    assert "Base" in env_content
    assert "Base.metadata" in env_content

    # Step 2: Create migration
    result = runner.invoke(app, ["makemigrations", "create users table"], env=env)
    assert result.exit_code == 0, f"Makemigrations failed: {result.stdout}"
    assert "Migration created" in result.stdout

    versions_dir = Path("migrations/versions")
    migration_files = list(versions_dir.glob("*.py"))
    assert len(migration_files) == 1

    migration_content = migration_files[0].read_text()
    assert "create users table" in migration_content
    assert "def upgrade()" in migration_content
    assert "def downgrade()" in migration_content

    # Step 3: Apply migration
    result = runner.invoke(app, ["migrate"], env=env)
    assert result.exit_code == 0, f"Migrate failed: {result.stdout}"

    # Verify table was created in database
    engine = create_engine(f"sqlite:///{db_path}")
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    assert "users" in tables

    columns = [col["name"] for col in inspector.get_columns("users")]
    assert "id" in columns
    assert "name" in columns
    assert "email" in columns

    # Step 4: Check current revision
    result = runner.invoke(app, ["current"], env=env)
    assert result.exit_code == 0, f"Current failed: {result.stdout}"
    assert "Current revision" in result.stdout

    # Step 5: Check history
    result = runner.invoke(app, ["history"], env=env)
    assert result.exit_code == 0, f"History failed: {result.stdout}"

    # Step 6: Downgrade
    result = runner.invoke(app, ["downgrade"], env=env)
    assert result.exit_code == 0, f"Downgrade failed: {result.stdout}"

    # Verify table was dropped
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    assert "users" not in tables


def test_makemigrations_with_invalid_message(setup_test_project):
    """Test makemigrations with special characters in message"""
    temp_dir, db_path = setup_test_project
    env = {"DATABASE_URL": f"sqlite:///{db_path}"}

    runner.invoke(app, ["init"], env=env)
    result = runner.invoke(app, ["makemigrations", "add@user#table!"], env=env)
    assert result.exit_code == 0


def test_history_with_no_migrations(setup_test_project):
    """Test history command with no migrations"""
    temp_dir, db_path = setup_test_project
    env = {"DATABASE_URL": f"sqlite:///{db_path}"}

    runner.invoke(app, ["init"], env=env)
    result = runner.invoke(app, ["history"], env=env)
    assert result.exit_code == 0
    assert "No migrations found" in result.stdout


def test_current_with_no_migrations(setup_test_project):
    """Test current command with no applied migrations"""
    temp_dir, db_path = setup_test_project
    env = {"DATABASE_URL": f"sqlite:///{db_path}"}

    runner.invoke(app, ["init"], env=env)
    result = runner.invoke(app, ["current"], env=env)
    assert result.exit_code == 0
    assert "No migrations applied" in result.stdout
