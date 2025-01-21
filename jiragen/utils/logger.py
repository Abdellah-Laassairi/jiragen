import sys
from pathlib import Path
from typing import Optional

from loguru import logger


def setup_logging(
    verbose: bool = False, log_file: Optional[Path] = None
) -> None:
    """Configure logging based on verbosity level and set up file logging.

    Args:
        verbose: If True, set logging level to DEBUG, otherwise INFO
        log_file: Path to the log file. If None, only console logging is configured
    """
    # Remove default handler
    logger.remove()

    # Add custom handler with appropriate level
    level = "DEBUG" if verbose else "ERROR"

    # Format for different levels and outputs
    format_debug = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    format_error = "<level>{level: <8}</level> | <level>{message}</level>"
    format_file = "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}"

    # Console logging with colors
    console_format = format_debug if verbose else format_error
    logger.add(sys.stderr, format=console_format, level=level, colorize=True)
    # File logging if path is provided
    if log_file is not None:
        try:
            # Create parent directory if it doesn't exist
            log_file.parent.mkdir(parents=True, exist_ok=True)

            # Add file logger with rotation
            logger.add(
                str(log_file),
                format=format_file,
                level="DEBUG",  # Always log debug to file for troubleshooting
                rotation="10 MB",  # Rotate when file reaches 10MB
                retention="1 week",  # Keep logs for 1 week
                compression="gz",  # Compress rotated logs
                backtrace=True,  # Include backtrace in error logs
                diagnose=True,  # Include variables in error logs
                enqueue=True,  # Thread-safe logging
            )
        except Exception as e:
            logger.warning(
                f"Failed to setup file logging at {log_file}: {str(e)}"
            )
