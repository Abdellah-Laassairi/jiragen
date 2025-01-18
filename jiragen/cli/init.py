"""Init command for jiragen CLI."""

import configparser
import sys
from pathlib import Path

from rich.console import Console

from jiragen.core.config import ConfigManager

console = Console()


def init_command(config_path: Path) -> None:
    """Initialize jiragen configuration."""
    try:
        config_manager = ConfigManager(config_path)

        if config_path.exists():
            existing_config = configparser.ConfigParser()
            existing_config.read(config_path)

            if "JIRA" not in existing_config:
                console.print(
                    f"[red]Error: Invalid configuration file format at {config_path}[/]"
                )
                sys.exit(1)

            config_manager.update_config(
                "JIRA",
                url=existing_config["JIRA"].get("url", ""),
                username=existing_config["JIRA"].get("username", ""),
                api_token=existing_config["JIRA"].get("api_token", ""),
                default_project=existing_config["JIRA"].get(
                    "default_project", ""
                ),
                default_assignee=existing_config["JIRA"].get(
                    "default_assignee", ""
                ),
            )

            console.print(
                f"[green]Configuration initialized using existing file at {config_path}[/]"
            )
            return

        console.print("\n[bold]Please enter your JIRA configuration:[/]")

        config_fields = {
            "url": "JIRA URL",
            "username": "Username",
            "api_token": "API Token",
            "default_project": "Default Project",
            "default_assignee": "Default Assignee",
        }

        config_values = {}
        for field, prompt in config_fields.items():
            while True:
                value = console.input(f"{prompt}: ")
                if value.strip():
                    config_values[field] = value
                    break
                console.print(
                    "[yellow]This field cannot be empty. Please provide a value.[/]"
                )

        config_manager.create_default_config()
        config_manager.update_config("JIRA", **config_values)

        console.print(
            f"\n[green]Configuration initialized successfully at {config_path}[/]"
        )

    except Exception as e:
        console.print(f"[red]Error initializing configuration: {str(e)}[/]")
        sys.exit(1)
