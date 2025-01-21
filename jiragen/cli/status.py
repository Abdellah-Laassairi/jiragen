"""Status command for jiragen CLI."""

from pathlib import Path
from typing import Any, Dict, Optional, Set

from loguru import logger
from rich import print as rprint
from rich.tree import Tree

from jiragen.core.client import VectorStoreClient


def normalize_path(path: Path) -> Path:
    """Normalize path to remove double slashes and clean up root representation."""
    return path.absolute().resolve()


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
        # Get tree data
        tree_data = store.get_stored_files()

        # Create root node
        root_label = "[bold]Vector DB Contents"
        if compact:
            root_label += " (Compact View)"
        if depth is not None:
            root_label += f" (Depth {depth})"

        root = Tree(root_label)

        # Handle empty or invalid data gracefully
        if not tree_data or not isinstance(tree_data, dict):
            root.add("[yellow]No valid data available from vector store[/]")
            rprint(root)
            return

        # Print tree structure
        print_tree(tree_data, root, compact=compact, max_depth=depth)
        rprint(root)

        # Show summary for valid data in compact mode
        if compact and isinstance(tree_data, dict):
            files = tree_data.get("files", set())
            directories = tree_data.get("directories", set())
            if isinstance(files, set) and isinstance(directories, set):
                rprint(
                    f"\nSummary: {len(files)} files in {len(directories)} directories"
                )

    except Exception as e:
        logger.error(f"Error displaying status: {str(e)}")
        rprint(f"[red]Error displaying status: {str(e)}[/]")
