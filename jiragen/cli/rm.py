"""Rm command for jiragen CLI."""

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
            rel_path = item.relative_to(cwd)
            if not gitignore.match_file(str(rel_path)):
                collected_paths.append(item)
    elif path_str == "*":
        # Only collect files in current directory
        for item in cwd.glob("*"):
            rel_path = item.relative_to(cwd)
            if not gitignore.match_file(str(rel_path)):
                collected_paths.append(item)
    else:
        # Handle specific path
        path = cwd / Path(path_str)
        if path.exists():
            rel_path = path.relative_to(cwd)
            if not gitignore.match_file(str(rel_path)):
                collected_paths.append(path)

    return collected_paths


def _process_files(progress, task, expanded_paths, store, cwd: Path) -> None:
    """Process the collected files and remove them from the store."""
    start_time = time.time()
    processed_count = 0

    # Update progress bar total
    progress.update(task, total=len(expanded_paths))

    if expanded_paths:
        for _ in expanded_paths:
            # Simulate processing file
            time.sleep(0.01)  # Simulate processing delay
            processed_count += 1
            progress.update(task, advance=1)

        removed_files = store.remove_files(expanded_paths)

        elapsed_time = time.time() - start_time
        speed = processed_count / elapsed_time if elapsed_time > 0 else 0

        if removed_files:
            tree = Tree(
                f"[bold red]Removed files ({processed_count} at {speed:.2f} files/second)"
            )
            for file in removed_files:
                try:
                    relative_path = file.resolve().relative_to(cwd)
                    tree.add(f"[red]- {relative_path}[/]")
                except ValueError:
                    tree.add(f"[red]- {file.resolve()}[/]")
            console.print(tree)
        else:
            console.print("\n[yellow]No files were removed[/]")
    else:
        console.print("\n[yellow]No files found matching the criteria[/]")


def rm_files_command(store, paths: List[str]) -> None:
    """Remove files from the vector database, respecting .gitignore patterns."""
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
            _process_files(progress, task, expanded_paths, store, cwd)

        except KeyboardInterrupt:
            console.print("\n[yellow]Operation cancelled by user[/]")
            sys.exit(1)
        except Exception as e:
            console.print(f"\n[red]Error: {str(e)}[/]")
            sys.exit(1)
