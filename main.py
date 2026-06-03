import sys
import shutil
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console


from src.dedup.dirTraversal import dirTraversal
from src.dedup.fileStats import fileStats
from src.dedup.fileHash import fileHash
from src.clustering.fileContent import FileContent
from src.clustering.embeddings import embeddings
from src.clustering.dbscanModel import dbScanModel
from src.clustering.dirNaming import DirNaming

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

@app.command(name="sort")
def sort(
    directory: Annotated[ Path,typer.Argument(
            exists=True,
            file_okay=False,
            dir_okay=True,
            readable=True,
            resolve_path=True,
        ),
    ]
):
    console.print(f"[bold green]Starting Vortex sort pipeline on {directory}...[/bold green]")

    console.print("[cyan]Phase 1: Traversing directory and identifying duplicates...[/cyan]")
    traverser = dirTraversal(directory)
    rel_paths, abs_paths = traverser.traverseDir()
    
    if not abs_paths:
        console.print("[yellow]No files found in the directory.[/yellow]")
        return

    hasher = fileHash()
    hashes = hasher.hashFiles((rel_paths, abs_paths))
    
    unique_files = []
    duplicates = []
    
    for file_hash, paths in hashes.items():
        unique_files.append(paths[0])
        if len(paths) > 1:
            duplicates.extend(paths[1:])
            
    if duplicates:
        console.print(f"[yellow]Found {len(duplicates)} exact duplicates. Removing...[/yellow]")
        for dup in duplicates:
            try:
                dup.unlink()
                console.print(f"Removed duplicate: {dup.name}")
            except Exception as e:
                console.print(f"[red]Failed to remove {dup.name}: {e}[/red]")
    else:
        console.print("[green]No duplicates found.[/green]")


if __name__ == "__main__":
    app()
