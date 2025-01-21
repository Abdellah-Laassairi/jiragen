"""Configuration management for jiragen."""

import configparser
from pathlib import Path
from typing import Optional

DEFAULT_CONFIG = {
    "JIRA": {
        "url": "",
        "username": "",
        "api_token": "",
        "default_project": "",
        "default_assignee": "",
    }
}


class ConfigManager:
    """Manages jiragen configuration."""

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize configuration manager.

        Args:
            config_path: Optional path to config file. If not provided,
                       defaults to ~/.jiragen/config.ini
        """
        self.config_path = (
            config_path or Path.home() / ".jiragen" / "config.ini"
        )
        self.config = configparser.ConfigParser()

        # Create config directory if it doesn't exist
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        # Load existing config if it exists, otherwise create default
        if self.config_path.exists():
            self.load_config()
        else:
            self.create_default_config()

    def create_default_config(self) -> None:
        """Create default configuration file."""
        self.config.read_dict(DEFAULT_CONFIG)
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, "w") as f:
            self.config.write(f)

    def load_config(self) -> None:
        """Load configuration from file."""
        if not self.config_path.exists():
            raise FileNotFoundError(
                f"Configuration file not found at {self.config_path}"
            )
        self.config.read(self.config_path)

    def update_config(self, section: str, **kwargs) -> None:
        """Update configuration values."""
        if not self.config.has_section(section):
            self.config.add_section(section)
        for key, value in kwargs.items():
            self.config.set(section, key, value)
        with open(self.config_path, "w") as f:
            self.config.write(f)


if __name__ == "__main__":
    config = ConfigManager()
    config.update_config("jiragen", username="jiragen", api_token="123")
    print(config.config)
