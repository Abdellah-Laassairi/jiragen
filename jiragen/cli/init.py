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
    """Prompt user for configuration values."""
    config = {}

    # JIRA Configuration
    console.print("\n[bold cyan]JIRA Configuration:[/]")
    jira_fields = {
        "url": "JIRA URL (e.g., https://your-domain.atlassian.net)",
        "username": "Username (usually your email)",
        "api_token": "API Token",
        "default_project": "Default Project Key",
        "default_assignee": "Default Assignee",
    }

    for field, prompt in jira_fields.items():
        env_var = f"JIRAGEN_{field.upper()}"
        if os.getenv(env_var):
            config[("JIRA", field)] = os.getenv(env_var)
            console.print(
                f"[green]Using {field} from environment variable {env_var}[/]"
            )
            continue

        while True:
            value = console.input(f"{prompt}: ")
            if value.strip() or Confirm.ask(f"Leave {field} empty?"):
                config[("JIRA", field)] = value
                break
            console.print(
                "[yellow]This field cannot be empty. Please provide a value.[/]"
            )

    # LLM Configuration
    console.print("\n[bold cyan]LLM Configuration:[/]")
    llm_fields = {
        "model": ("Model name (default: openai/gpt-4o)", "openai/gpt-4o"),
        "temperature": ("Temperature (0.0-1.0, default: 0.7)", "0.7"),
        "max_tokens": ("Maximum tokens (default: 2000)", "2000"),
    }

    for field, (prompt, default) in llm_fields.items():
        env_var = f"JIRAGEN_LLM_{field.upper()}"
        if os.getenv(env_var):
            config[("llm", field)] = os.getenv(env_var)
            console.print(
                f"[green]Using {field} from environment variable {env_var}[/]"
            )
            continue

        value = console.input(f"{prompt}: ")
        config[("llm", field)] = value if value.strip() else default

    # Vector Store Configuration
    console.print("\n[bold cyan]Vector Store Configuration:[/]")
    vector_store_fields = {
        "path": (
            "Vector store path (default: .jiragen/vector_store)",
            ".jiragen/vector_store",
        ),
    }

    for field, (prompt, default) in vector_store_fields.items():
        env_var = f"JIRAGEN_VECTOR_STORE_{field.upper()}"
        if os.getenv(env_var):
            config[("vector_store", field)] = os.getenv(env_var)
            console.print(
                f"[green]Using {field} from environment variable {env_var}[/]"
            )
            continue

        value = console.input(f"{prompt}: ")
        config[("vector_store", field)] = value if value.strip() else default

    return config


def validate_config(config: configparser.ConfigParser) -> bool:
    """Validate configuration file format and required sections."""
    required_sections = {
        "JIRA": {
            "url",
            "username",
            "api_token",
            "default_project",
            "default_assignee",
        },
        "llm": {
            "model",
            "temperature",
            "max_tokens",
        },
        "vector_store": {
            "path",
        },
    }

    for section, fields in required_sections.items():
        if section not in config:
            return False
        if not all(field in config[section] for field in fields):
            return False

    return True


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

        # Get all configuration values
        config_values = prompt_for_config()

        # Create config directory if it doesn't exist
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # Group config values by section and update
        grouped_config = {}
        for (section, key), value in config_values.items():
            if section not in grouped_config:
                grouped_config[section] = {}
            grouped_config[section][key] = value

        # Update configuration for each section
        for section, values in grouped_config.items():
            config_manager.update_config(section, **values)

        console.print(
            f"\n[green]Configuration initialized successfully at {config_path}[/]"
        )

        # Display the configuration
        console.print("\n[bold]Current configuration:[/]")

        for section, values in grouped_config.items():
            console.print(f"\n[cyan]{section} Configuration:[/]")
            for key, value in values.items():
                if section == "JIRA" and key == "api_token":
                    value = "*" * len(value) if value else ""
                console.print(f"{key}: {value}")

    except Exception as e:
        console.print(f"[red]Error initializing configuration: {str(e)}[/]")
        sys.exit(1)
