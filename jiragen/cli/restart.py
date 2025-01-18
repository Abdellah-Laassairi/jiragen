"""restart command for jiragen CLI."""

import sys

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from jiragen.core.vector_store import VectorStoreClient

console = Console()


def restart_command(store: VectorStoreClient) -> None:
    """Restart the vector store service."""
    with Progress(
        SpinnerColumn("simpleDots"),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        try:
            progress.add_task("Restarting vector store service...", total=None)
            store.restart()
            console.print(
                "\n[green]Vector store service restarted successfully[/]"
            )
        except Exception as e:
            console.print(
                f"\n[red]Error restarting vector store service: {str(e)}[/]"
            )
            sys.exit(1)
