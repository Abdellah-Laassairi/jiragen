"""Miscellaneous utility functions for jiragen."""

from pathlib import Path

import pathspec
from loguru import logger


def read_gitignore(path: Path) -> pathspec.PathSpec:
    """Read .gitignore file and create a PathSpec object, including additional patterns."""
    gitignore_path = path / ".gitignore"
    patterns = []

    if gitignore_path.exists():
        logger.info(f"Reading .gitignore file from {gitignore_path}")
        with open(gitignore_path) as f:
            patterns = f.readlines()

    # Add custom patterns
    patterns.append(".git\n")  # Ensure ".git" is ignored
    patterns.append(".gitignore\n")  # Ensure ".gitignore" is ignored

    # Create PathSpec
    gitignore = pathspec.PathSpec.from_lines("gitwildmatch", patterns)
    return gitignore
