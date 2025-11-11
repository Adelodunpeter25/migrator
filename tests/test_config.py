import pytest

from migrator.utils.config_loader import ConfigLoader


def test_load_from_env(mock_env):
    """Test loading DATABASE_URL from environment"""
    mock_env("DATABASE_URL", "postgresql://test:test@localhost/test")

    url = ConfigLoader.load_database_url()
    assert url == "postgresql://test:test@localhost/test"


def test_load_from_sqlalchemy_env(mock_env):
    """Test loading SQLALCHEMY_DATABASE_URI from environment"""
    mock_env("SQLALCHEMY_DATABASE_URI", "sqlite:///test.db")

    url = ConfigLoader.load_database_url()
    assert url == "sqlite:///test.db"


def test_no_database_url_raises_error(monkeypatch):
    """Test error when no DATABASE_URL found"""
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("SQLALCHEMY_DATABASE_URI", raising=False)

    with pytest.raises(ValueError, match="DATABASE_URL not found"):
        ConfigLoader.load_database_url()
