"""Init command for jiragen CLI."""

import configparser
import os
import sys
from pathlib import Path

from loguru import logger
from rich.console import Console
from rich.prompt import Confirm

from jiragen.core.config import ConfigManager
from jiragen.utils.data import get_config_dir

console = Console()


def prompt_for_config(template_config=None) -> dict:
    """Prompt user for configuration values."""
    logger.debug("Starting prompt_for_config.")
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
            logger.info(
                f"JIRA '{field}' loaded from environment variable '{env_var}'."
            )
            continue

        # Get template value if available
        template_value = (
            template_config["JIRA"][field]
            if template_config and "JIRA" in template_config
            else ""
        )

        while True:
            value = console.input(
                f"{prompt} [{template_value}]: "
                if template_value
                else f"{prompt}: "
            )
            value = value if value.strip() else template_value
            if value.strip() or Confirm.ask(f"Leave {field} empty?"):
                config[("JIRA", field)] = value
                logger.debug(f"JIRA '{field}' set to '{value}'.")
                break
            console.print(
                "[yellow]This field cannot be empty. Please provide a value.[/]"
            )
            logger.warning(f"JIRA '{field}' left empty by user.")

    # LLM Configuration
    console.print("\n[bold cyan]LLM Configuration:[/]")
    llm_fields = {
        "model": ("Model name (default: openai/gpt-4o)", "openai/gpt-4o"),
        "api_base": ("API Base URL (optional, default based on model)", ""),
        "api_token": ("API Token (optional)", ""),
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
            logger.info(
                f"LLM '{field}' loaded from environment variable '{env_var}'."
            )
            continue

        # Get template value if available
        template_value = (
            template_config["llm"][field]
            if template_config and "llm" in template_config
            else default
        )

        value = console.input(
            f"{prompt} [{template_value}]: "
            if template_value
            else f"{prompt}: "
        )
        config_value = value if value.strip() else template_value
        config[("llm", field)] = config_value
        logger.debug(f"LLM '{field}' set to '{config_value}'.")

    logger.debug("Completed prompt_for_config.")
    return config


def validate_config(config: configparser.ConfigParser) -> bool:
    """Validate configuration file format and required sections."""
    logger.debug("Starting validate_config.")
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
            "api_base",
            "api_token",
            "temperature",
            "max_tokens",
        },
    }

    for section, fields in required_sections.items():
        if section not in config:
            logger.error(f"Missing required section: {section}")
            return False
        if not all(field in config[section] for field in fields):
            missing = fields - config[section].keys()
            logger.error(f"Missing fields {missing} in section '{section}'.")
            return False

    logger.debug("Configuration validation passed.")
    return True


def init_command(template_config_path: Path = None) -> None:
    """Initialize jiragen configuration.

    Args:
        template_config_path: Path to the template configuration file. If provided,
                    will be used as a template for the default config at ~/.config/jiragen/config.ini
    """
    logger.info(
        f"Initializing configuration with template path: {template_config_path}"
    )
    try:
        # Use get_config_dir() to get the standard config location
        final_config_path = get_config_dir() / "config.ini"
        config_manager = ConfigManager(final_config_path)

        # If a template config file is provided, use it directly
        if template_config_path is not None:
            if not template_config_path.exists():
                console.print(
                    f"[red]Error: Template configuration file not found at {template_config_path}[/]"
                )
                logger.error(
                    f"Template configuration file not found at {template_config_path}."
                )
                sys.exit(1)

            logger.debug("Loading template configuration.")
            template_config = configparser.ConfigParser()
            template_config.read(template_config_path)
            logger.info(
                f"Template configuration loaded from {template_config_path}."
            )

            if not validate_config(template_config):
                console.print(
                    f"[red]Error: Invalid template configuration file format at {template_config_path}[/]"
                )
                logger.error(
                    f"Invalid template configuration format at {template_config_path}."
                )
                sys.exit(1)

            console.print(
                f"[green]Using template configuration from {template_config_path}[/]"
            )
            logger.info(
                f"Using template configuration from {template_config_path}."
            )

            # Create config directory if it doesn't exist
            final_config_path.parent.mkdir(parents=True, exist_ok=True)
            logger.debug(
                f"Ensured configuration directory exists at {final_config_path.parent}."
            )

            # Copy all sections and values from template to final config
            grouped_config = {}
            for section in template_config.sections():
                grouped_config[section] = dict(template_config[section])
                config_manager.update_config(
                    section, **grouped_config[section]
                )
                logger.info(
                    f"Updated configuration section '{section}' with template values"
                )

        else:
            # If no template and default config exists, check if we want to update it
            if final_config_path.exists():
                logger.debug("Configuration file already exists.")
                if not Confirm.ask(
                    "Configuration file already exists. Would you like to update it?"
                ):
                    console.print("[yellow]Using existing configuration.[/]")
                    logger.info(
                        "User chose to use existing configuration without updating."
                    )
                    return

            # Get all configuration values through prompts
            config_values = prompt_for_config(None)

            # Create config directory if it doesn't exist
            final_config_path.parent.mkdir(parents=True, exist_ok=True)
            logger.debug(
                f"Ensured configuration directory exists at {final_config_path.parent}."
            )

            # Group config values by section and update
            grouped_config = {}
            for (section, key), value in config_values.items():
                if section not in grouped_config:
                    grouped_config[section] = {}
                grouped_config[section][key] = value

            # Update configuration for each section
            for section, values in grouped_config.items():
                config_manager.update_config(section, **values)
                logger.info(
                    f"Updated configuration section '{section}' with values: {values}"
                )

        console.print(
            f"\n[green]Configuration initialized successfully at {final_config_path}[/]"
        )
        logger.success(
            f"Configuration initialized successfully at {final_config_path}."
        )

        # Display the configuration
        console.print("\n[bold]Current configuration:[/]")
        logger.debug("Displaying current configuration.")

        for section, values in grouped_config.items():
            console.print(f"\n[cyan]{section} Configuration:[/]")
            for key, value in values.items():
                # Mask both JIRA and LLM API tokens
                if key == "api_token" or (
                    section == "JIRA" and key == "api_token"
                ):
                    masked_value = "*" * len(value) if value else ""
                    console.print(f"{key}: {masked_value}")
                    logger.debug(
                        f"Displayed masked value for '{section}.{key}'."
                    )
                else:
                    console.print(f"{key}: {value}")
                    logger.debug(
                        f"Displayed value for '{section}.{key}': {value}"
                    )

    except Exception as e:
        console.print(f"[red]Error initializing configuration: {str(e)}[/]")
        logger.exception(
            "Exception occurred during configuration initialization."
        )
        sys.exit(1)
