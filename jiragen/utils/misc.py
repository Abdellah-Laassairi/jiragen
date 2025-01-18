"""Miscellaneous utility functions for jiragen."""

import sys
from pathlib import Path

import pathspec
from loguru import logger


def read_gitignore(path: Path) -> pathspec.PathSpec:
    """Read .gitignore file and create a PathSpec object, including additional patterns."""
    gitignore_path = path / ".gitignore"
    patterns = []

    if gitignore_path.exists():
        with open(gitignore_path) as f:
            patterns = f.readlines()

    # Add custom patterns
    patterns.append(".git\n")  # Ensure ".git" is ignored

    # Create PathSpec
    gitignore = pathspec.PathSpec.from_lines("gitwildmatch", patterns)
    return gitignore


def setup_logging(verbose: bool = False) -> None:
    """Configure logging based on verbosity level.

    Args:
        verbose: If True, set logging level to DEBUG, otherwise INFO
    """
    # Remove default handler
    logger.remove()

    # Add custom handler with appropriate level
    level = "DEBUG" if verbose else "INFO"

    # Format for different levels
    format_debug = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    format_info = "<level>{level: <8}</level> | <level>{message}</level>"

    # Use appropriate format based on level
    log_format = format_debug if verbose else format_info

    # Add handler with custom format
    logger.add(sys.stderr, format=log_format, level=level, colorize=True)
