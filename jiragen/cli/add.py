"""Add command for jiragen CLI."""

import sys
import time
from pathlib import Path
from typing import List

from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)
from rich.tree import Tree

from jiragen.utils.misc import read_gitignore

console = Console()


def _collect_paths(cwd: Path, path_str: str, gitignore) -> List[Path]:
    """Collect paths based on the given path string, respecting gitignore patterns."""
    collected_paths = []

    if path_str in (".", "**"):
        # Recursively collect all files
        for item in cwd.rglob("*"):
            if item.is_file():  # Only add files, not directories
                rel_path = item.relative_to(cwd)
                if not gitignore.match_file(str(rel_path)):
                    collected_paths.append(item)
    elif path_str == "*":
        # Only collect files in current directory
        for item in cwd.glob("*"):
            if item.is_file():  # Only add files, not directories
                rel_path = item.relative_to(cwd)
                if not gitignore.match_file(str(rel_path)):
                    collected_paths.append(item)
    else:
        # Handle specific path
        path = cwd / Path(path_str)
        if path.exists():
            if path.is_file():
                rel_path = path.relative_to(cwd)
                if not gitignore.match_file(str(rel_path)):
                    collected_paths.append(path)
            elif path.is_dir():
                # If it's a directory, collect all files recursively
                for item in path.rglob("*"):
                    if item.is_file():  # Only add files, not directories
                        rel_path = item.relative_to(cwd)
                        if not gitignore.match_file(str(rel_path)):
                            collected_paths.append(item)

    return collected_paths


def _process_files(progress, task, expanded_paths, store) -> None:
    """Process the collected files and add them to the store."""
    start_time = time.time()

    if expanded_paths:
        # Add files to store
        added_files = store.add_files(expanded_paths)
        processed_count = len(added_files)

        elapsed_time = time.time() - start_time
        speed = processed_count / elapsed_time if elapsed_time > 0 else 0

        # Create tree view of added files
        root = Tree("📁 Added Files")
        for file in added_files:
            root.add(f"[green]{file}[/]")

        console.print("\n")
        console.print(root)
        console.print(
            f"\n[green]Successfully added {processed_count} files "
            f"({speed:.1f} files/second)[/]"
        )

        # Update progress bar with actual count
        progress.update(task, total=processed_count, completed=processed_count)
    else:
        console.print("\n[yellow]No files to add[/]")


def add_files_command(store, paths: List[str]) -> None:
    """Add files to the vector database, respecting .gitignore patterns."""
    cwd = Path.cwd().resolve()
    expanded_paths = []

    # Read .gitignore patterns
    gitignore = read_gitignore(cwd)

    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        "[bold blue]{task.completed} files",
        TimeElapsedColumn(),
        TimeRemainingColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Processing files...", total=None)

        try:
            # Collect all paths
            for path_str in paths:
                expanded_paths.extend(_collect_paths(cwd, path_str, gitignore))

            # Filter out directories, only keep files
            expanded_paths = [p for p in expanded_paths if p.is_file()]

            # Process the files
            _process_files(progress, task, expanded_paths, store)

        except KeyboardInterrupt:
            console.print("\n[yellow]Operation cancelled by user[/]")
            sys.exit(1)
        except Exception as e:
            console.print(f"\n[red]Error: {str(e)}[/]")
            sys.exit(1)
