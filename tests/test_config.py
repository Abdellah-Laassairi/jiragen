"""Unit tests for the configuration management functionality."""

import os
import tempfile
from pathlib import Path

import pytest

from jiragen.core.config import ConfigManager


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        old_cwd = os.getcwd()
        os.chdir(tmpdirname)
        yield Path(tmpdirname)
        os.chdir(old_cwd)


def test_config_manager_initialization(temp_dir):
    """Test that ConfigManager initializes correctly."""
    config_path = temp_dir / ".jiragen" / "config.ini"
    config_manager = ConfigManager(config_path=config_path)
    assert config_manager.config_path == config_path


def test_config_manager_create_default_config(temp_dir):
    """Test that ConfigManager creates default config correctly."""
    config_path = temp_dir / ".jiragen" / "config.ini"
    config_manager = ConfigManager(config_path=config_path)
    config_manager.create_default_config()

    assert config_manager.config_path.exists()
    assert config_manager.config_path.is_file()


def test_config_manager_load_config(temp_dir):
    """Test that ConfigManager loads config correctly."""
    config_path = temp_dir / ".jiragen" / "config.ini"
    config_manager = ConfigManager(config_path=config_path)
    config_manager.create_default_config()

    # Load the config
    config_manager.load_config()

    # Check that basic sections exist
    assert "JIRA" in config_manager.config
    assert "url" in config_manager.config["JIRA"]
    assert "username" in config_manager.config["JIRA"]
    assert "api_token" in config_manager.config["JIRA"]
