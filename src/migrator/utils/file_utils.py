from pathlib import Path
from typing import Optional


def read_template(template_name: str) -> str:
    """Read template file content"""
    template_path = Path(__file__).parent.parent / "templates" / template_name
    if not template_path.exists():
        raise FileNotFoundError(f"Template {template_name} not found")
    return template_path.read_text()


def write_file(path: Path, content: str) -> None:
    """Write content to file"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def find_latest_migration(migrations_dir: Path) -> Optional[Path]:
    """Find the latest migration file"""
    versions_dir = migrations_dir / "versions"
    if not versions_dir.exists():
        return None

    migration_files = sorted(versions_dir.glob("*.py"), reverse=True)
    return migration_files[0] if migration_files else None
