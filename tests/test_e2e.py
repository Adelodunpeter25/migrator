from pathlib import Path

import pytest
from typer.testing import CliRunner

from migrator.cli import app

runner = CliRunner()


@pytest.fixture
def setup_test_project(temp_dir):
    """Setup a test project with models"""
    # Create .env file
    env_file = temp_dir / ".env"
    env_file.write_text("DATABASE_URL=sqlite:///test.db")

    # Create models.py
    models_file = temp_dir / "models.py"
    models_file.write_text(
        """
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    email = Column(String(100))
"""
    )

    yield temp_dir


def test_full_migration_workflow(setup_test_project):
    """Test complete migration workflow: init -> makemigrations -> migrate"""
    # Test init
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0
    assert Path("migrations").exists()
    assert Path("migrations/versions").exists()

    # Verify env.py was created with Base import
    env_py = Path("migrations/env.py")
    assert env_py.exists()
    env_content = env_py.read_text()
    assert "Base" in env_content
