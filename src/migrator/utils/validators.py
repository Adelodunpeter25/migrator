import re


def validate_database_url(url: str) -> bool:
    """Validate database URL format"""
    pattern = r"^(postgresql|mysql|sqlite|oracle|mssql)(\+\w+)?://.*"
    return bool(re.match(pattern, url, re.IGNORECASE))


def validate_revision_id(revision: str) -> bool:
    """Validate revision ID format"""
    if revision in ["head", "base", "-1"]:
        return True
    return bool(re.match(r"^[a-f0-9]{12}$", revision))


def sanitize_message(message: str) -> str:
    """Sanitize migration message"""
    return re.sub(r"[^\w\s-]", "", message).strip()
