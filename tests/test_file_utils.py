import pytest

from migrator.utils.file_utils import (
    find_latest_migration,
    read_template,
    write_file,
)


def test_read_template_env_py():
    """Test reading env.py template"""
    content = read_template("env.py.mako")
    assert "from alembic import context" in content
    assert "${imports}" in content


def test_read_template_script_py():
    """Test reading script.py template"""
    content = read_template("script.py.mako")
    assert "def upgrade()" in content
    assert "def downgrade()" in content


def test_read_template_not_found():
    """Test reading non-existent template"""
    with pytest.raises(FileNotFoundError):
        read_template("nonexistent.mako")


def test_write_file(temp_dir):
    """Test writing file"""
    file_path = temp_dir / "test" / "file.txt"
    write_file(file_path, "test content")

    assert file_path.exists()
    assert file_path.read_text() == "test content"


def test_find_latest_migration_empty(temp_dir):
    """Test finding migration in empty directory"""
    migrations_dir = temp_dir / "migrations"
    migrations_dir.mkdir()

    result = find_latest_migration(migrations_dir)
    assert result is None


def test_find_latest_migration(temp_dir):
    """Test finding latest migration"""
    migrations_dir = temp_dir / "migrations"
    versions_dir = migrations_dir / "versions"
    versions_dir.mkdir(parents=True)

    # Create migration files
    (versions_dir / "001_first.py").write_text("")
    (versions_dir / "002_second.py").write_text("")

    result = find_latest_migration(migrations_dir)
    assert result is not None
    assert result.name == "002_second.py"
