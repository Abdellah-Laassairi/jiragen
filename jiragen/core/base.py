from abc import ABC, abstractmethod
from typing import Optional

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn


class BaseCommand(ABC):
    """Base class for all CLI commands"""

    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()

    @abstractmethod
    def execute(self, *args, **kwargs) -> None:
        """Execute the command"""
        pass

    def create_progress(self, description: str) -> Progress:
        """Create a standard progress bar"""
        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        )

    def handle_error(self, error: Exception, message: str) -> None:
        """Standard error handling"""
        self.console.print(f"[red]Error: {message} - {str(error)}[/]")
        raise error
