"""Init command for jiragen CLI."""

import configparser
import os
import sys
from pathlib import Path

from rich.console import Console
from rich.prompt import Confirm

from jiragen.core.config import ConfigManager

console = Console()


def prompt_for_config() -> dict:
    """Prompt user for JIRA configuration values."""
    console.print("\n[bold]Please enter your JIRA configuration:[/]")

    config_fields = {
        "url": "JIRA URL (e.g., https://your-domain.atlassian.net)",
        "username": "Username (usually your email)",
        "api_token": "API Token",
        "default_project": "Default Project Key",
        "default_assignee": "Default Assignee",
    }

    config_values = {}
    for field, prompt in config_fields.items():
        # Check for environment variables first
        env_var = f"JIRAGEN_{field.upper()}"
        if os.getenv(env_var):
            config_values[field] = os.getenv(env_var)
            console.print(
                f"[green]Using {field} from environment variable {env_var}[/]"
            )
            continue

        while True:
            value = console.input(f"{prompt}: ")
            if value.strip() or Confirm.ask(f"Leave {field} empty?"):
                config_values[field] = value
                break
            console.print(
                "[yellow]This field cannot be empty. Please provide a value.[/]"
            )

    return config_values


def validate_config(config: configparser.ConfigParser) -> bool:
    """Validate configuration file format and required sections."""
    if "JIRA" not in config:
        return False

    required_fields = {
        "url",
        "username",
        "api_token",
        "default_project",
        "default_assignee",
    }
    return all(field in config["JIRA"] for field in required_fields)


def init_command(config_path: Path) -> None:
    """Initialize jiragen configuration.

    Args:
        config_path: Path to the configuration file. If not provided,
                    defaults to ~/.jiragen/config.ini
    """
    try:
        config_manager = ConfigManager(config_path)

        # If config exists, validate and ask to overwrite
        if config_path.exists():
            existing_config = configparser.ConfigParser()
            existing_config.read(config_path)

            if not validate_config(existing_config):
                console.print(
                    f"[yellow]Warning: Invalid configuration file format at {config_path}[/]"
                )
                if not Confirm.ask(
                    "Would you like to create a new configuration?"
                ):
                    console.print("[red]Initialization cancelled.[/]")
                    sys.exit(1)
            else:
                if not Confirm.ask(
                    "Configuration file already exists. Would you like to overwrite it?"
                ):
                    console.print("[yellow]Using existing configuration.[/]")
                    return

        # Get configuration values
        config_values = prompt_for_config()

        # Create config directory if it doesn't exist
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # Update configuration
        config_manager.update_config("JIRA", **config_values)

        console.print(
            f"\n[green]Configuration initialized successfully at {config_path}[/]"
        )

        # Display the configuration
        console.print("\n[bold]Current configuration:[/]")
        for key, value in config_values.items():
            if key == "api_token":
                value = "*" * len(value) if value else ""
            console.print(f"{key}: {value}")

    except Exception as e:
        console.print(f"[red]Error initializing configuration: {str(e)}[/]")
        sys.exit(1)
