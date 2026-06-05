import shutil
from pathlib import Path
from typing import Annotated
import logging

import typer
from rich.console import Console
from rich.table import Table
from rich import box

from vortiq.dedup.dirTraversal import dirTraversal
from vortiq.dedup.fileHash import fileHash
from vortiq.clustering.fileContent import FileContent
from vortiq.clustering.embeddings import embeddings
from vortiq.clustering.dbscanModel import dbScanModel
from vortiq.clustering.dirNaming import DirNaming

app = typer.Typer(help="Vortex CLI - File Organization Tool")
console = Console()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S')

@app.command(name="help", help="Display help information about Vortex CLI.")
def custom_help(ctx: typer.Context):
    """
    Display help information.
    """
    console.print("Vortex CLI - Available Commands")
    console.print("  sort  - Sort a directory by deduplicating and clustering files")
    console.print("  help  - Show this help message")

@app.command(name="sort", help="Sort and organize a directory by deduplicating and clustering files.")
def sort(
    directory: Annotated[ Path,typer.Argument(
            help="The directory path to sort.",
            exists=True,
            file_okay=False,
            dir_okay=True,
            readable=True,
            resolve_path=True,
        ),
    ]
):
    console.print("Starting Vortex sort pipeline")
    console.print(f"Target Directory: {directory}")
    console.print("-" * 40)

    console.print("[Step 1/5] Traversing directory and identifying files...")
    traverser = dirTraversal(directory)
    rel_paths, abs_paths = traverser.traverseDir()
    
    if not abs_paths:
        console.print("No files found in the directory. Exiting.")
        return
        
    logging.info(f"Discovered {len(abs_paths)} files in the target directory.")

    console.print("\n[Step 2/5] Hashing files to identify duplicates...")
    hasher = fileHash()
    hashes = hasher.hashFiles((rel_paths, abs_paths))
    
    unique_files = []
    duplicates = []
    
    for file_hash, paths in hashes.items():
        unique_files.append(paths[0])
        if len(paths) > 1:
            duplicates.extend(paths[1:])
            
    if duplicates:
        console.print(f"Found {len(duplicates)} exact duplicates. Removing...")
        dup_table = Table(show_header=True, box=box.SIMPLE)
        dup_table.add_column("File Name")
        dup_table.add_column("Status", justify="right")
        for dup in duplicates:
            try:
                dup.unlink()
                dup_table.add_row(dup.name, "Removed")
                logging.info(f"Removed duplicate file: {dup.name}")
            except Exception as e:
                dup_table.add_row(dup.name, f"Failed: {e}")
                logging.error(f"Failed to remove duplicate {dup.name}: {e}")
        console.print(dup_table)
    else:
        console.print("No exact duplicates found.")

    console.print("\n" + "-" * 40)
    console.print("[Step 3/5] Extracting content and generating embeddings...")

    qdrant_db_path = Path("./qdrant_db")
    if qdrant_db_path.exists():
        shutil.rmtree(qdrant_db_path)

    emb = embeddings()
    content_extractor = FileContent()
    id_to_path = {}
    
    for i, path in enumerate(unique_files):
        ext = path.suffix.lower()
        point_id = i + 1
        id_to_path[point_id] = path
        
        logging.info(f"Processing file {i+1}/{len(unique_files)}: {path.name}")
        
        if ext in content_extractor.img:
            try:
                emb.insert_image(point_id=point_id, image_path=str(path))
            except Exception as e:
                logging.error(f"Error embedding image {path.name}: {e}")
        else:
            try:
                text_content = content_extractor.extract(path)
                if text_content and text_content.strip():
                    emb.insert_text(point_id=point_id, file_content=text_content)
                else:
                    logging.info(f"No extractable text found in {path.name}")
            except Exception as e:
                logging.error(f"Error embedding text from {path.name}: {e}")
                
    console.print("\n" + "-" * 40)
    console.print("[Step 4/5] Running DBSCAN clustering and generating directory names...")
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

    namer = DirNaming()
    cluster_names = namer.generate_names(cluster_to_files)
    logging.info(f"Generated {len(cluster_names)} cluster names.")
    
    console.print("\n" + "-" * 40)
    console.print("[Step 5/5] Reorganizing Files...")
    
    summary_table = Table(show_header=True, box=box.SIMPLE)
    summary_table.add_column("Cluster / Folder")
    summary_table.add_column("Files Moved", justify="right")

    for label, files in cluster_items:
        folder_name = cluster_names.get(label, f"Cluster_{label}")

        target_dir = directory / folder_name
        target_dir.mkdir(exist_ok=True)

        moved_count = 0
        for file_path in files:
            if not file_path.exists():
                continue
            new_path = target_dir / file_path.name
            if new_path != file_path:
                try:
                    shutil.move(str(file_path), str(new_path))
                    moved_count += 1
                    logging.info(f"Moved {file_path.name} -> {folder_name}/")
                except Exception as e:
                    logging.error(f"Error moving {file_path.name}: {e}")
        
        if moved_count > 0:
            summary_table.add_row(folder_name, str(moved_count))

    console.print(summary_table)
    console.print("-" * 40)
    console.print("Sorting completed successfully!")
    
if __name__ == "__main__":
    app()
