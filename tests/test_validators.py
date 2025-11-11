from migrator.utils.validators import (
    sanitize_message,
    validate_database_url,
    validate_revision_id,
)


def test_validate_database_url_postgresql():
    """Test PostgreSQL URL validation"""
    assert validate_database_url("postgresql://user:pass@localhost/db")
    assert validate_database_url("postgresql+psycopg2://user:pass@localhost/db")


def test_validate_database_url_sqlite():
    """Test SQLite URL validation"""
    assert validate_database_url("sqlite:///test.db")
    assert validate_database_url("sqlite:///./app.db")


def test_validate_database_url_mysql():
    """Test MySQL URL validation"""
    assert validate_database_url("mysql://user:pass@localhost/db")
    assert validate_database_url("mysql+pymysql://user:pass@localhost/db")


def test_validate_database_url_invalid():
    """Test invalid database URLs"""
    assert not validate_database_url("invalid://url")
    assert not validate_database_url("not-a-url")


def test_validate_revision_id_special():
    """Test special revision IDs"""
    assert validate_revision_id("head")
    assert validate_revision_id("base")
    assert validate_revision_id("-1")


def test_validate_revision_id_hash():
    """Test hash revision IDs"""
    assert validate_revision_id("abc123def456")
    assert not validate_revision_id("invalid")
    assert not validate_revision_id("abc")


def test_sanitize_message():
    """Test message sanitization"""
    assert sanitize_message("add user table") == "add user table"
    assert sanitize_message("add-user_table") == "add-user_table"
    assert sanitize_message("add@user#table!") == "addusertable"
