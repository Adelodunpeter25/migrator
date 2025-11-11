from typer.testing import CliRunner

from migrator.cli import app

runner = CliRunner()


def test_cli_help():
    """Test CLI help command"""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Migrator" in result.stdout


def test_init_help():
    """Test init command help"""
    result = runner.invoke(app, ["init", "--help"])
    assert result.exit_code == 0
    assert "Initialize migration environment" in result.stdout


def test_makemigrations_help():
    """Test makemigrations command help"""
    result = runner.invoke(app, ["makemigrations", "--help"])
    assert result.exit_code == 0
    assert "Create new migration" in result.stdout


def test_migrate_help():
    """Test migrate command help"""
    result = runner.invoke(app, ["migrate", "--help"])
    assert result.exit_code == 0
    assert "Apply migrations" in result.stdout


def test_downgrade_help():
    """Test downgrade command help"""
    result = runner.invoke(app, ["downgrade", "--help"])
    assert result.exit_code == 0
    assert "Rollback migrations" in result.stdout


def test_history_help():
    """Test history command help"""
    result = runner.invoke(app, ["history", "--help"])
    assert result.exit_code == 0
    assert "Show migration history" in result.stdout


def test_current_help():
    """Test current command help"""
    result = runner.invoke(app, ["current", "--help"])
    assert result.exit_code == 0
    assert "Show current revision" in result.stdout


def test_stamp_help():
    """Test stamp command help"""
    result = runner.invoke(app, ["stamp", "--help"])
    assert result.exit_code == 0
    assert "Mark database as migrated" in result.stdout


def test_status_help():
    """Test status command help"""
    result = runner.invoke(app, ["status", "--help"])
    assert result.exit_code == 0
    assert "Show migration status" in result.stdout
