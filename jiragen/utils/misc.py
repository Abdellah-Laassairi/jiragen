"""Miscellaneous utility functions for jiragen."""

from pathlib import Path

import pathspec


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
