"""Kill command for jiragen CLI."""

import os
import signal
import subprocess
from pathlib import Path

from loguru import logger


def find_service_pid() -> list[int]:
    """Find the PID of the vector store service process."""
    try:
        # Use ps to find python processes running vector_store_service.py
        cmd = ["pgrep", "-f", "vector_store_service.py"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0 and result.stdout:
            return [int(pid) for pid in result.stdout.splitlines()]
        return []
    except Exception as e:
        logger.error(f"Error finding service PID: {e}")
        return []


def kill_command() -> None:
    """Kill the vector store service."""
    try:
        # Find service PIDs
        pids = find_service_pid()

        if not pids:
            logger.info("No vector store service processes found")
            return

        # Kill each process
        for pid in pids:
            try:
                os.kill(pid, signal.SIGTERM)
                logger.info(f"Sent SIGTERM to process {pid}")
            except ProcessLookupError:
                logger.debug(f"Process {pid} not found")
            except Exception as e:
                logger.error(f"Error killing process {pid}: {e}")

        # Clean up socket file if it exists
        socket_path = Path.home() / ".jiragen" / "vector_store.sock"
        if socket_path.exists():
            socket_path.unlink()
            logger.debug("Removed socket file")

        logger.info("Vector store service killed successfully")
    except Exception as e:
        logger.error(f"Error killing vector store service: {e}")
        raise Exception(
            f"Failed to kill vector store service: {str(e)}"
        ) from e
