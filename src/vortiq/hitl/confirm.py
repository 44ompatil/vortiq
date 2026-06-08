from typing import List, Tuple, Dict
from pathlib import Path
import typer
from rich.console import Console
from rich.table import Table
from rich import box

console = Console()

def confirm_clustering(cluster_items: List[Tuple[int, List[Path]]], cluster_names: Dict[int, str]) -> bool:
    """
    Displays the proposed clustering and asks the user for confirmation.
    """
    console.print("\n" + "=" * 40)
    console.print("[bold cyan]Proposed File Organization[/bold cyan]")
    console.print("=" * 40)

    for label, files in cluster_items:
        folder_name = cluster_names.get(label, f"Cluster_{label}")
        
        table = Table(show_header=True, box=box.ROUNDED, title=f"Folder: [bold green]{folder_name}[/bold green]")
        table.add_column("File Name", style="cyan")
        table.add_column("Original Path", style="dim")
        
        for file_path in files:
            table.add_row(file_path.name, str(file_path.parent))
            
        console.print(table)
        console.print()

    console.print("=" * 40)
    
    return typer.confirm("Do you want to proceed with moving the files as shown above?")
