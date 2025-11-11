from rich.console import Console

console = Console()


def success(message: str):
    """Display success message"""
    console.print(f"✅ {message}", style="green")


def error(message: str):
    """Display error message"""
    console.print(f"❌ {message}", style="red")


def info(message: str):
    """Display info message"""
    console.print(f"➜ {message}", style="blue")


def warning(message: str):
    """Display warning message"""
    console.print(f"⚠️  {message}", style="yellow")
