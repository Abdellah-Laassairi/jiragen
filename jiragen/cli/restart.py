"""restart command for jiragen CLI."""

import sys
import time

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from jiragen.cli.kill import kill_command
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

            # First kill any existing processes
            kill_command()

            # Wait a bit for processes to clean up
            time.sleep(1)

            # Ensure service is running and ready
            store.ensure_service_running()

            # Wait for service to be fully initialized
            time.sleep(2)

            # Send a ping to verify service is ready
            try:
                store.send_command("ping")
            except Exception as e:
                console.print(
                    f"\n[red]Service not ready after restart: {str(e)}[/]"
                )
                sys.exit(1)

            console.print(
                "\n[green]Vector store service restarted successfully[/]"
            )
        except Exception as e:
            console.print(
                f"\n[red]Error restarting vector store service: {str(e)}[/]"
            )
            sys.exit(1)
