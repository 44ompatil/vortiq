import shutil
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console


from src.dedup.dirTraversal import dirTraversal
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
    console.print(f"[bold green]-> Starting Vortex sort pipeline on {directory}...[/bold green]")

    console.print("[cyan]-> Traversing directory and identifying duplicates...[/cyan]")
    traverser = dirTraversal(directory)
    rel_paths, abs_paths = traverser.traverseDir()
    
    if not abs_paths:
        console.print("[yellow]-> No files found in the directory.[/yellow]")
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
        console.print(f"[yellow]-> Found {len(duplicates)} exact duplicates. Removing...[/yellow]")
        for dup in duplicates:
            try:
                dup.unlink()
                console.print(f"-> Removed duplicate: {dup.name}")
            except Exception as e:
                console.print(f"[red]-> Failed to remove {dup.name}: {e}[/red]")
    else:
        console.print("[green]-> No duplicates found.[/green]")

    console.print("[cyan]-> Generating embeddings and clustering...[/cyan]")

    qdrant_db_path = Path("./qdrant_db")
    if qdrant_db_path.exists():
        shutil.rmtree(qdrant_db_path)

    emb = embeddings()
    
    content_extractor = FileContent()
    id_to_path = {}
    
    with console.status("-> Extracting content and generating embeddings..."):
        for i, path in enumerate(unique_files):
            ext = path.suffix.lower()
            point_id = i + 1
            id_to_path[point_id] = path
            
            if ext in content_extractor.img:
                try:
                    emb.insert_image(point_id=point_id, image_path=str(path))
                except Exception as e:
                    console.print(f"[red]-> Error embedding image {path.name}: {e}[/red]")
            else:
                try:
                    text_content = content_extractor.extract(path)
                    if text_content and text_content.strip():
                        emb.insert_text(point_id=point_id, file_content=text_content)
                except Exception as e:
                    console.print(f"[red]-> Error embedding text from {path.name}: {e}[/red]")
                    
    console.print("[cyan]-> Running DBSCAN clustering...[/cyan]")
    emb.client.close()
    dbscan = dbScanModel()
    labels_dict = dbscan.predict_all()
    
    cluster_to_files = {}
    
    if "text_labels" in labels_dict and len(labels_dict["text_labels"]) > 0:
        for i, label in enumerate(labels_dict["text_labels"]):
            pt_id = dbscan.txtPtId[i]
            if pt_id in id_to_path:
                cluster_to_files.setdefault(label, []).append(id_to_path[pt_id])
                
    if "image_labels" in labels_dict and len(labels_dict["image_labels"]) > 0:
        max_txt_label = max(labels_dict["text_labels"]) if len(labels_dict["text_labels"]) > 0 else 0
        offset = max_txt_label + 1
        
        for i, label in enumerate(labels_dict["image_labels"]):
            pt_id = dbscan.imgPtId[i]
            if pt_id in id_to_path:
                final_label = label if label == -1 else label + offset
                cluster_to_files.setdefault(final_label, []).append(id_to_path[pt_id])
    
    processed_paths = set()
    for files in cluster_to_files.values():
        processed_paths.update(files)

    unprocessed_files = [p for p in unique_files if p not in processed_paths]
    if unprocessed_files:
        cluster_to_files.setdefault(-1, []).extend(unprocessed_files)

    cluster_items = [(label, list(files)) for label, files in cluster_to_files.items()]
    console.print("[cyan]-> Generating directory names...[/cyan]")
    namer = DirNaming()
    cluster_names = namer.generate_names(cluster_to_files)
    
    console.print("[cyan]-> Reorganizing files...[/cyan]")
    for label, files in cluster_items:
        folder_name = cluster_names.get(label, f"Cluster_{label}")

        target_dir = directory / folder_name
        target_dir.mkdir(exist_ok=True)

        for file_path in files:
            if not file_path.exists():
                console.print(f"[yellow]-> Skipping {file_path.name}: already moved.[/yellow]")
                continue
            new_path = target_dir / file_path.name
            if new_path != file_path:
                try:
                    shutil.move(str(file_path), str(new_path))
                    console.print(f"Moved {file_path.name} -> [green]{folder_name}/[/green]")
                except Exception as e:
                    console.print(f"[red]-> Error moving {file_path.name}: {e}[/red]")
                    
    console.print("[bold green]-> Sorting completed successfully![/bold green]")
    
if __name__ == "__main__":
    app()
