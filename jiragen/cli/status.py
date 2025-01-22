"""Status command for jiragen CLI."""

import os
from pathlib import Path
from typing import Any, Dict, Optional, Set

from loguru import logger
from rich import print as rprint
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree

from jiragen.core.client import VectorStoreClient, VectorStoreConfig
from jiragen.utils.data import get_runtime_dir


def normalize_path(path: Path) -> Path:
    """Normalize path to remove double slashes and clean up root representation."""
    return path.absolute().resolve()


def get_file_stats(files: Set[Path]) -> Dict[str, Any]:
    """Get statistics about the files in the collection."""
    total_size = 0
    total_words = 0
    total_lines = 0
    file_types = {}

    for file in files:
        if file.exists():
            # Get file size
            size = os.path.getsize(file)
            total_size += size

            # Get file extension
            ext = file.suffix.lower()
            if ext:
                file_types[ext] = file_types.get(ext, 0) + 1

            # Count words and lines
            try:
                content = file.read_text()
                words = len(content.split())
                lines = len(content.splitlines())
                total_words += words
                total_lines += lines
            except Exception as e:
                logger.warning(f"Could not read file {file}: {e}")

    return {
        "total_size": total_size,
        "total_words": total_words,
        "total_lines": total_lines,
        "file_types": file_types,
        "num_files": len(files),
    }


def format_size(size: int) -> str:
    """Format size in bytes to human readable format."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


def print_stats_table(stats: Dict[str, Any], title: str) -> None:
    """Print a table with collection statistics."""
    table = Table(title=title, show_header=True, header_style="bold magenta")

    # Add statistics
    table.add_column("Metric", style="cyan")
    table.add_column("Value", justify="right", style="green")

    table.add_row("Total Files", str(stats["num_files"]))
    table.add_row("Total Size", format_size(stats["total_size"]))
    table.add_row("Total Words", f"{stats['total_words']:,}")
    table.add_row("Total Lines", f"{stats['total_lines']:,}")

    # Add file type distribution if any
    if stats["file_types"]:
        table.add_section()
        table.add_row("File Types", "Count")
        for ext, count in sorted(
            stats["file_types"].items(), key=lambda x: x[1], reverse=True
        ):
            table.add_row(ext, str(count))

    rprint(table)


def print_tree_recursive(
    tree_dict: Dict[str, Any],
    tree_node: Tree,
    prefix: str = "",
    compact: bool = False,
) -> None:
    """Recursively print tree structure with compact mode support."""
    files = sorted(tree_dict.get("files", []))
    dirs = sorted(tree_dict.get("dirs", {}).keys())

    if compact and (len(files) > 3 or len(dirs) > 3):
        if dirs:
            dir_node = tree_node.add(f"[bold blue]{len(dirs)} directories[/]")
            for dir_name in dirs[:3]:
                subdir_node = dir_node.add(f"[bold blue]{dir_name}/[/]")
                if tree_dict["dirs"][dir_name].get("files") or tree_dict[
                    "dirs"
                ][dir_name].get("dirs"):
                    subdir_node.add("[dim]...[/]")
            if len(dirs) > 3:
                dir_node.add("[dim]...[/]")

        if files:
            file_node = tree_node.add(f"[green]{len(files)} files[/]")
            for file_name in files[:3]:
                file_node.add(f"[green]{file_name}[/]")
            if len(files) > 3:
                file_node.add("[dim]...[/]")
    else:
        for dir_name in dirs:
            dir_node = tree_node.add(f"[bold blue]{dir_name}/[/]")
            print_tree_recursive(
                tree_dict["dirs"][dir_name],
                dir_node,
                f"{prefix}/{dir_name}",
                compact,
            )

        for file_name in files:
            tree_node.add(f"[green]{file_name}[/]")


def build_tree_structure(
    files: Set[Path], max_depth: Optional[int] = None
) -> Dict[str, Dict[str, Any]]:
    """Build hierarchical tree structure with depth limit support."""
    root = {"files": [], "dirs": {}}

    for file in files:
        file = normalize_path(file)
        current = file

        path_parts = []
        while current != current.parent:
            path_parts.append(current)
            current = current.parent

        path_parts = path_parts[::-1]

        if max_depth is not None:
            path_parts = path_parts[: max_depth + 1]

        current_dict = root
        for part in path_parts[:-1]:
            if part.name not in current_dict["dirs"]:
                current_dict["dirs"][part.name] = {"files": [], "dirs": {}}
            current_dict = current_dict["dirs"][part.name]

        if file.is_file():
            if max_depth is None or len(path_parts) <= max_depth + 1:
                current_dict["files"].append(file.name)
            elif "..." not in current_dict["files"]:
                current_dict["files"].append("...")

    return root


def print_tree(
    tree_data: Dict[str, Set[Path]],
    parent: Tree,
    compact: bool = False,
    max_depth: Optional[int] = None,
) -> None:
    """Print tree structure with comprehensive validation."""
    try:
        if not isinstance(tree_data, dict):
            parent.add("[yellow]Invalid data structure from vector store[/]")
            return

        files = tree_data.get("files", set())
        directories = tree_data.get("directories", set())

        if not isinstance(files, set) or not isinstance(directories, set):
            parent.add(
                "[yellow]Invalid data types in vector store response[/]"
            )
            return

        if not files and not directories:
            parent.add("[yellow]No files in database[/]")
            return

        hierarchy = build_tree_structure(files, max_depth)
        print_tree_recursive(hierarchy, parent, compact=compact)

    except Exception as e:
        logger.error(f"Error building tree structure: {str(e)}")
        raise


def status_command(
    store: VectorStoreClient,
    compact: bool = False,
    depth: Optional[int] = None,
) -> None:
    """Display vector store status with comprehensive validation."""
    try:
        runtime_dir = get_runtime_dir()

        # Initialize both stores
        codebase_store = VectorStoreClient(
            VectorStoreConfig(
                collection_name="codebase_content",
                db_path=runtime_dir / "codebase_data" / "vector_db",
            )
        )
        jira_store = VectorStoreClient(
            VectorStoreConfig(
                collection_name="jira_content",
                db_path=runtime_dir / "jira_data" / "vector_db",
            )
        )

        # Get tree data for both stores
        codebase_data = codebase_store.get_stored_files()
        jira_data = jira_store.get_stored_files()

        # Create root nodes with emojis
        codebase_root = Tree("🗂  [bold cyan]Codebase Vector DB Contents")
        jira_root = Tree("📋 [bold magenta]JIRA Vector DB Contents")

        if compact:
            codebase_root.label += " (Compact View)"
            jira_root.label += " (Compact View)"
        if depth is not None:
            codebase_root.label += f" (Depth {depth})"
            jira_root.label += f" (Depth {depth})"

        # Print tree structures
        print_tree(
            codebase_data, codebase_root, compact=compact, max_depth=depth
        )
        print_tree(jira_data, jira_root, compact=compact, max_depth=depth)

        # Print both trees
        rprint("\n")
        rprint(Panel(codebase_root, border_style="cyan"))
        rprint("\n")
        rprint(Panel(jira_root, border_style="magenta"))
        rprint("\n")

        # Get and display statistics
        codebase_files = codebase_data.get("files", set())
        jira_files = jira_data.get("files", set())

        if codebase_files or jira_files:
            rprint(
                Panel("[bold]📊 Collection Statistics[/]", border_style="green")
            )

            if codebase_files:
                codebase_stats = get_file_stats(codebase_files)
                print_stats_table(codebase_stats, "🗂  Codebase Collection")
                rprint("\n")

            if jira_files:
                jira_stats = get_file_stats(jira_files)
                print_stats_table(jira_stats, "📋 JIRA Collection")

    except Exception as e:
        logger.error(f"Error displaying status: {str(e)}")
        rprint(f"[red]Error displaying status: {str(e)}[/]")
