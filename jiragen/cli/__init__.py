"""CLI module for jiragen."""

from .add import add_files_command
from .clean import clean_command
from .fetch import fetch_command
from .generate import generate_issue
from .init import init_command
from .rm import rm_files_command
from .status import status_command
from .upload import upload_command

__all__ = [
    "add_files_command",
    "clean_command",
    "rm_files_command",
    "init_command",
    "status_command",
    "fetch_command",
    "upload_command",
    "generate_issue",
]
