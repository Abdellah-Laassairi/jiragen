"""Fetch & store JIRA data"""

import sys
import time
from pathlib import Path
from typing import List

from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)
from rich.table import Table
from rich.text import Text

from jiragen.core.config import ConfigManager
from jiragen.core.vector_store import VectorStoreClient, VectorStoreConfig
from jiragen.services.jira import JiraConfig, JiraDataManager, JiraFetchConfig

console = Console()


def create_progress() -> Progress:
    """Create a custom progress bar with enhanced features."""
    return Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(bar_width=40),
        TaskProgressColumn(),
        TextColumn("[progress.percentage]{task.completed}/{task.total}"),
        TimeElapsedColumn(),
        TimeRemainingColumn(),
        console=console,
        expand=True,
    )


def fetch_command(
    config_manager: ConfigManager, query: str | None, types: List[str] | None
) -> None:
    """Fetch data from JIRA and store it in a separate vector store.

    Args:
        config_manager: The configuration manager instance
        query: The JIRA query to fetch data. If None, fetches all data for specified types
        types: List of data types to fetch (epics, tickets, components)
    """
    try:
        start_time = time.time()

        # Handle empty query - fetch all data
        if not query or not query.strip():
            console.print(
                "\n[bold blue]No query provided - fetching all data[/]"
            )
            query = ""  # Empty query will fetch all data
        else:
            console.print(f"\n[bold]Fetching JIRA data with query: {query}[/]")

        # Handle types
        if not types:
            types = ["epics", "tickets", "components"]
            console.print("[blue]No types specified - fetching all types[/]")

        # Initialize configurations
        jira_config = JiraConfig.from_config_manager(config_manager)
        fetch_config = JiraFetchConfig(
            output_dir=Path(".jiragen") / "jira_data", data_types=types
        )

        # Create output directory
        fetch_config.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize JIRA vector store
        jira_store_config = VectorStoreConfig(
            repo_path=fetch_config.output_dir, collection_name="jira_content"
        )
        jira_store = VectorStoreClient(jira_store_config)

        # Initialize JIRA manager
        jira_manager = JiraDataManager(jira_config, fetch_config)
        progress_data = {}

        with create_progress() as progress:
            # Create tasks with placeholder totals
            tasks = {
                data_type: progress.add_task(
                    f"[cyan]Fetching {data_type}...", total=100
                )
                for data_type in types
            }

            # Define progress callback
            def update_progress(
                data_type: str, percent: float, current: int, total: int
            ):
                if data_type not in progress_data:
                    progress_data[data_type] = {"total": total}
                task_id = tasks[data_type]
                # Update total if it has changed
                if progress.tasks[task_id].total != total:
                    progress.update(task_id, total=total)
                progress.update(task_id, completed=current)
                progress.update(
                    task_id,
                    description=f"[cyan]Fetching {data_type}... ({current}/{total})",
                )

            # Set the progress callback
            jira_manager.progress_callback = update_progress

            # Start fetching data
            results = jira_manager.fetch_data(jira_store)

            # Update final status
            for data_type, count in results.items():
                task_id = tasks[data_type]
                if count > 0:  # Only update if items were fetched
                    progress.update(task_id, completed=count)
                progress.update(
                    task_id,
                    description=f"[green]✓ {data_type} completed ({count} items)",
                )

        end_time = time.time()
        duration = end_time - start_time

        # Create statistics table
        table = Table(
            title="JIRA Fetch Statistics",
            show_header=True,
            header_style="bold magenta",
        )
        table.add_column("Data Type", style="cyan")
        table.add_column("Items Fetched", justify="right", style="green")

        total_items = 0
        for data_type, count in results.items():
            table.add_row(data_type.capitalize(), str(count))
            total_items += count

        table.add_row("Total", f"[bold]{total_items}[/bold]", style="bold")

        # Print summary
        console.print("\n")
        console.print(table)

        summary = Text()
        summary.append(
            "\n✨ Fetch completed successfully!\n", style="bold green"
        )
        summary.append(
            f"⏱️  Time taken: {duration:.2f} seconds\n", style="blue"
        )
        summary.append(
            f"📁 Data stored in: {fetch_config.output_dir}\n", style="yellow"
        )
        console.print(summary)

    except Exception as e:
        console.print(f"[red]Error fetching JIRA data: {str(e)}[/]")
        sys.exit(1)
