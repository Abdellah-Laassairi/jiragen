"""Configuration management for jiragen."""

import configparser
from pathlib import Path
from typing import Optional

from loguru import logger

from jiragen.utils.data import get_config_dir

DEFAULT_CONFIG = {
    "JIRA": {
        "url": "",
        "username": "",
        "api_token": "",
        "default_project": "",
        "default_assignee": "",
    },
    "llm": {
        "model": "openai/gpt-4o",
        "temperature": "0.7",
        "max_tokens": "2000",
        "api_base": "",  # Base URL for API endpoint
        "api_token": "",  # API token for authentication
    },
}


class ConfigManager:
    """Manages jiragen configuration."""

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize configuration manager.

        Args:
            config_path: Optional path to config file. If not provided,
                       defaults to standard config location based on OS.
        """
        if config_path is None:
            config_dir = get_config_dir()
            config_path = config_dir / "config.ini"
            logger.debug(
                f"No config path provided, using default: {config_path}"
            )

        # Resolve home directory if present
        self.config_path = config_path.expanduser()
        self.config = configparser.ConfigParser()
        logger.info(
            f"Initializing ConfigManager with path: {self.config_path}"
        )

        # Create config directory if it doesn't exist
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        logger.debug(
            f"Ensured config directory exists: {self.config_path.parent}"
        )

        # Load existing config if it exists, otherwise create default
        if self.config_path.exists():
            logger.debug("Found existing config file, loading it")
            self.load_config()
        else:
            logger.info(
                "No existing config found, creating default configuration"
            )
            self.create_default_config()

    def create_default_config(self) -> None:
        """Create default configuration file."""
        logger.info("Creating default configuration")
        self.config.read_dict(DEFAULT_CONFIG)
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, "w") as f:
            self.config.write(f)
        logger.debug(f"Default configuration written to {self.config_path}")

    def load_config(self) -> None:
        """Load configuration from file."""
        if not self.config_path.exists():
            logger.error(f"Configuration file not found at {self.config_path}")
            raise FileNotFoundError(
                f"Configuration file not found at {self.config_path}"
            )
        logger.info(f"Loading configuration from {self.config_path}")
        self.config.read(self.config_path)
        logger.debug("Configuration loaded successfully")

    def update_config(self, section: str, **kwargs) -> None:
        """Update configuration values."""
        logger.info(f"Updating configuration section: {section}")
        if not self.config.has_section(section):
            logger.debug(f"Creating new section: {section}")
            self.config.add_section(section)
        for key, value in kwargs.items():
            logger.debug(f"Setting {section}.{key} = {value}")
            self.config.set(section, key, value)
        with open(self.config_path, "w") as f:
            self.config.write(f)
        logger.info("Configuration updated and saved successfully")
