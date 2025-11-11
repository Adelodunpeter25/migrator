from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(help="🧩 Migrator - Universal Migration CLI")
console = Console()


@app.command()
def init(
    directory: Path = typer.Option(Path("migrations"), "--dir", "-d", help="Migration directory")
):
    """Initialize migration environment"""
    console.print("🚀 Initializing migration environment...")


@app.command()
def makemigrations(
    message: str = typer.Argument(..., help="Migration description"),
    autogenerate: bool = typer.Option(True, "--auto/--manual", help="Auto-generate migration")
):
    """Create new migration"""
    console.print(f"📝 Creating migration: {message}")


@app.command()
def migrate(
    revision: str = typer.Option("head", "--revision", "-r", help="Target revision")
):
    """Apply migrations"""
    console.print("⬆️  Applying migrations...")


@app.command()
def downgrade(
    revision: str = typer.Option("-1", "--revision", "-r", help="Target revision")
):
    """Rollback migrations"""
    console.print("⬇️  Rolling back migrations...")


@app.command()
def history():
    """Show migration history"""
    table = Table(title="Migration History")
    table.add_column("Revision", style="cyan")
    table.add_column("Message", style="white")
    table.add_column("Status", style="green")
    console.print(table)


@app.command()
def current():
    """Show current revision"""
    console.print("📍 Current revision: None")
