import sys
import time
from pathlib import Path
from typing import List

from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.table import Table
from rich.text import Text

from jiragen.core.config import ConfigManager
from jiragen.core.vector_store import VectorStoreClient, VectorStoreConfig
from jiragen.services.jira import JiraConfig, JiraDataManager, JiraFetchConfig

console = Console()


def fetch_command(config_manager: ConfigManager, types: List[str]) -> None:
    """Fetch data from JIRA and store it in a separate vector store."""
    try:
        start_time = time.time()
        console.print("\n[bold]Fetching JIRA data...[/]")

        # Handle 'all' type by expanding it to all available types
        if "all" in types:
            types = ["epics", "tickets", "components"]
            console.print(
                "[blue]'all' specified - fetching epics, tickets, and components[/]"
            )

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

        # Initialize JIRA manager and fetch data
        jira_manager = JiraDataManager(jira_config, fetch_config)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("Fetching JIRA data...", total=None)
            results = jira_manager.fetch_data(jira_store)
            progress.update(task, completed=100)

        # Calculate elapsed time
        elapsed_time = time.time() - start_time

        # Create statistics table
        table = Table(
            title="JIRA Fetch Statistics",
            show_header=True,
            header_style="bold magenta",
        )
        table.add_column("Type", style="cyan")
        table.add_column("Items Fetched", justify="right", style="green")

        total_items = 0
        for data_type, count in results.items():
            table.add_row(data_type.capitalize(), str(count))
            total_items += count

        # Add summary row
        table.add_row("Total", f"[bold]{total_items}[/bold]", style="bold")

        # Create summary panel
        summary = Text()
        summary.append(
            "\n✨ Fetch completed successfully!\n", style="bold green"
        )
        summary.append(
            f"⏱️  Time taken: {elapsed_time:.2f} seconds\n", style="blue"
        )
        summary.append(
            f"📁 Data stored in: {fetch_config.output_dir}\n", style="yellow"
        )

        # Display results
        console.print("\n")
        console.print(table)
        console.print(Panel(summary, title="Summary", border_style="green"))

    except Exception as e:
        console.print(f"[red]Error fetching JIRA data: {str(e)}[/]")
        sys.exit(1)
