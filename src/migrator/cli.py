from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from migrator.core.alembic_backend import AlembicBackend
from migrator.core.config import MigratorConfig
from migrator.core.detector import ModelDetector
from migrator.core.logger import error, info, success
from migrator.utils.validators import sanitize_message, validate_database_url

app = typer.Typer(help="🧩 Migrator - Universal Migration CLI")
console = Console()


@app.command()
def init(
    directory: Path = typer.Option(Path("migrations"), "--dir", "-d", help="Migration directory")
):
    """Initialize migration environment"""
    try:
        info("Detecting project configuration...")
        config = MigratorConfig.load(migrations_dir=directory)

        info("Finding SQLAlchemy Base...")
        base = ModelDetector.find_base()
        if not base:
            error("Could not find SQLAlchemy Base class")
            raise typer.Exit(1)

        # Get the module where Base was actually defined (not sqlalchemy)
        import inspect

        base_module = inspect.getmodule(base)
        if base_module and not base_module.__name__.startswith("sqlalchemy"):
            config.base_import_path = f"{base_module.__name__}.Base"
        else:
            # Fallback: scan for the file that has Base
            for py_file in Path.cwd().rglob("*.py"):
                if "venv" in str(py_file) or "site-packages" in str(py_file):
                    continue
                try:
                    content = py_file.read_text()
                    if (
                        "Base = declarative_base()" in content
                        or "Base=declarative_base()" in content
                    ):
                        module_name = py_file.stem
                        config.base_import_path = f"{module_name}.Base"
                        break
                except Exception:
                    continue

        info(f"Initializing migrations in {directory}...")
        backend = AlembicBackend(config)
        backend.init(directory)

        success(f"Migration environment created at {directory}")
        console.print("\n📁 Structure:")
        console.print(f"  {directory}/")
        console.print("  ├── versions/")
        console.print("  ├── env.py")
        console.print("  ├── script.py.mako")
        console.print("  └── alembic.ini")

    except Exception as e:
        error(f"Initialization failed: {e}")
        raise typer.Exit(1)


@app.command()
def makemigrations(
    message: str = typer.Argument(..., help="Migration description"),
    autogenerate: bool = typer.Option(True, "--auto/--manual", help="Auto-generate migration"),
):
    """Create new migration"""
    try:
        config = MigratorConfig.load()

        if not validate_database_url(config.database_url):
            error("Invalid database URL format")
            raise typer.Exit(1)

        message = sanitize_message(message)
        if not message:
            error("Migration message cannot be empty")
            raise typer.Exit(1)

        backend = AlembicBackend(config)

        info(f"Creating migration: {message}")
        migration_path = backend.create_migration(message, autogenerate)

        success(f"Migration created: {migration_path}")

    except Exception as e:
        error(f"Migration creation failed: {e}")
        raise typer.Exit(1)


@app.command()
def migrate(revision: str = typer.Option("head", "--revision", "-r", help="Target revision")):
    """Apply migrations"""
    try:
        config = MigratorConfig.load()
        backend = AlembicBackend(config)

        current = backend.current()
        info(f"Current revision: {current or 'None'}")
        info(f"Upgrading to: {revision}")

        backend.apply_migrations(revision)

        success("Database up-to-date")

    except Exception as e:
        error(f"Migration failed: {e}")
        raise typer.Exit(1)


@app.command()
def downgrade(revision: str = typer.Option("-1", "--revision", "-r", help="Target revision")):
    """Rollback migrations"""
    try:
        config = MigratorConfig.load()
        backend = AlembicBackend(config)

        current = backend.current()
        info(f"Current revision: {current}")
        info(f"Downgrading to: {revision}")

        backend.downgrade(revision)

        success("Rollback complete")

    except Exception as e:
        error(f"Downgrade failed: {e}")
        raise typer.Exit(1)


@app.command()
def history():
    """Show migration history"""
    try:
        config = MigratorConfig.load()
        backend = AlembicBackend(config)

        migrations = backend.history()
        current = backend.current()

        if not migrations:
            info("No migrations found")
            return

        table = Table(title="Migration History")
        table.add_column("Revision", style="cyan")
        table.add_column("Message", style="white")
        table.add_column("Status", style="green")

        for migration in migrations:
            status = "✅ applied" if migration["revision"] == current else "⏳ pending"
            table.add_row(migration["revision"][:12], migration["message"], status)

        console.print(table)

    except Exception as e:
        error(f"Failed to get history: {e}")
        raise typer.Exit(1)


@app.command()
def current():
    """Show current revision"""
    try:
        config = MigratorConfig.load()
        backend = AlembicBackend(config)

        revision = backend.current()
        if revision:
            success(f"Current revision: {revision}")
        else:
            info("No migrations applied yet")

    except Exception as e:
        error(f"Failed to get current revision: {e}")
        raise typer.Exit(1)
