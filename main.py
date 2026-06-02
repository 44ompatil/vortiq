import typer
from rich.console import Console

app = typer.Typer(rich_markup_mode="rich", help="[bold cyan]Vortex CLI[/bold cyan] - File Organization Tool")
console = Console()

@app.command(name="help")
def custom_help(ctx: typer.Context):
    """
    Display help information.
    """
    console.print("[bold blue]Vortex CLI[/bold blue]")
    console.print("Available commands:")
    console.print("  [cyan]sort[/cyan]  - Sort a directory")
    console.print("  [cyan]help[/cyan]  - Show this help message")
    console.print("\nUse [bold]--help[/bold] for detailed usage instructions.")

if __name__ == "__main__":
    app()
