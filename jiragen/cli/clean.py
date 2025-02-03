"""Clean command for jiragen CLI."""

from pathlib import Path
from typing import Set

from loguru import logger
from rich.console import Console
from rich.prompt import Confirm
from rich.tree import Tree

from jiragen.core.client import VectorStoreClient, VectorStoreConfig
from jiragen.utils.data import get_runtime_dir

console = Console()


def clean_command() -> None:
    """Remove all files from the vector database.

    This command will completely clean both the codebase and JIRA vector databases,
    removing all stored files. Use with caution as this operation cannot be undone.
    """
    try:
        runtime_dir = get_runtime_dir()

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

        codebase_files = codebase_store.get_stored_files()
        jira_files = jira_store.get_stored_files()

        files_to_remove_codebase: Set[Path] = codebase_files.get(
            "files", set()
        )
        files_to_remove_jira: Set[Path] = jira_files.get("files", set())

        if not files_to_remove_codebase and not files_to_remove_jira:
            console.print(
                "[yellow]Both vector stores are already empty.[/yellow]"
            )
            return

        console.print(
            "[bold red]Warning: This will remove all files from both the codebase and JIRA vector databases.[/bold red]"
        )
        console.print("[bold red]This action cannot be undone.[/bold red]")

        if files_to_remove_codebase:
            tree = Tree("[bold red]Codebase files to be removed")
            for file in sorted(files_to_remove_codebase):
                tree.add(f"[red]{file}[/red]")
            console.print(tree)

        if files_to_remove_jira:
            tree = Tree("[bold red]JIRA files to be removed")
            for file in sorted(files_to_remove_jira):
                tree.add(f"[red]{file}[/red]")
            console.print(tree)

        if not Confirm.ask("\nDo you want to continue?"):
            console.print("[yellow]Operation cancelled.[/yellow]")
            return

        if files_to_remove_codebase:
            codebase_store.remove_files(list(files_to_remove_codebase))
            console.print("[green]✓ Cleaned codebase vector store[/green]")

        if files_to_remove_jira:
            jira_store.remove_files(list(files_to_remove_jira))
            console.print("[green]✓ Cleaned JIRA vector store[/green]")

        console.print(
            "[green bold]Successfully cleaned both vector stores[/green bold]"
        )

    except Exception as e:
        logger.exception("Failed to clean vector stores")
        console.print(f"[red]Error cleaning vector stores: {str(e)}[/red]")
