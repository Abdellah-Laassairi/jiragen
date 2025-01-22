"""Data utilities for jiragen."""

import os
from pathlib import Path


def get_config_dir() -> Path:
    """Get the configuration directory following XDG Base Directory specification.

    Returns:
        Path: ~/.config/jiragen
    """
    xdg_config = os.getenv("XDG_CONFIG_HOME")
    if xdg_config:
        base = Path(xdg_config)
    else:
        base = Path.home() / ".config"

    return (base / "jiragen").resolve()


def get_data_dir() -> Path:
    """Get the data directory following XDG Base Directory specification.

    Returns:
        Path: ~/.local/share/jiragen
    """
    xdg_data = os.getenv("XDG_DATA_HOME")
    if xdg_data:
        base = Path(xdg_data)
    else:
        base = Path.home() / ".local/share"

    return (base / "jiragen").resolve()


def get_runtime_dir() -> Path:
    """Get the runtime directory for temporary files.

    Returns:
        Path: $XDG_RUNTIME_DIR/jiragen or /tmp/jiragen as fallback
    """
    runtime_dir = os.getenv("XDG_RUNTIME_DIR")
    if runtime_dir:
        base = Path(runtime_dir)
    else:
        base = Path("/tmp")

    jiragen_runtime = (base / "jiragen").resolve()

    # Ensure the directory exists with proper permissions
    if not jiragen_runtime.exists():
        jiragen_runtime.mkdir(parents=True, mode=0o700)
    elif not jiragen_runtime.is_dir():
        jiragen_runtime.unlink()
        jiragen_runtime.mkdir(mode=0o700)

    # Ensure proper permissions even if directory already exists
    jiragen_runtime.chmod(0o700)

    return jiragen_runtime
