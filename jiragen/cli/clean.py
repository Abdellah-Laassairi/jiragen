"""Clean command for jiragen CLI."""

from pathlib import Path
from typing import Set

from loguru import logger
from rich.console import Console
from rich.tree import Tree

console = Console()


def clean_command(store) -> None:
    """Remove all files from the vector database.

    This command will completely clean the vector database, removing all stored files.
    Use with caution as this operation cannot be undone.

    Args:
        store: The vector store client instance
    """
    try:
        # Get current stored files before cleaning
        stored_files = store.get_stored_files()
        files_to_remove: Set[Path] = stored_files.get("files", set())

        if not files_to_remove:
            console.print("[yellow]Vector store is already empty.[/yellow]")
            return

        # Create a confirmation prompt
        console.print(
            "[bold red]Warning: This will remove all files from the vector database.[/bold red]"
        )
        console.print("[bold red]This action cannot be undone.[/bold red]")

        # Show what will be removed
        tree = Tree("[bold red]Files to be removed")
        for file in sorted(files_to_remove):
            tree.add(f"[red]{file}[/red]")
        console.print(tree)

        # Ask for confirmation
        if (
            not console.input("\nDo you want to continue? [y/N]: ")
            .lower()
            .startswith("y")
        ):
            console.print("[yellow]Operation cancelled.[/yellow]")
            return

        # Remove all files
        removed = store.remove_files(list(files_to_remove))

        if removed:
            console.print(
                f"[green]Successfully removed {len(removed)} files from the vector store.[/green]"
            )
        else:
            console.print("[yellow]No files were removed.[/yellow]")

    except Exception as e:
        logger.error(f"Error during clean operation: {str(e)}")
        console.print(f"[red]Failed to clean vector store: {str(e)}[/red]")
