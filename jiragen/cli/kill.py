"""Kill command for jiragen CLI."""

import os
import signal
import subprocess
import time

from loguru import logger

from jiragen.utils.data import get_runtime_dir


def find_service_pid() -> list[int]:
    """Find the PID of the vector store service process."""
    try:
        # Use ps to find python processes running vector_store.py
        cmd = ["pgrep", "-f", "vector_store.py"]
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
        # Get runtime directory from utils
        runtime_dir = get_runtime_dir()
        socket_path = runtime_dir / "vector_store.sock"
        lock_file = runtime_dir / "vector_store.lock"

        # Find service PIDs
        pids = find_service_pid()

        if not pids:
            logger.info("No vector store service processes found")
            return

        # First try graceful shutdown
        if socket_path.exists():
            try:
                import pickle
                import socket

                sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                sock.settimeout(2)  # 2 second timeout
                sock.connect(str(socket_path))
                request = {"command": "kill"}
                sock.sendall(pickle.dumps(request))
                sock.close()
                logger.debug("Sent kill command to service")
            except Exception as e:
                logger.debug(f"Failed to send kill command: {e}")

        # Wait a bit for graceful shutdown
        time.sleep(1)

        # Kill remaining processes
        remaining_pids = find_service_pid()
        for pid in remaining_pids:
            try:
                os.kill(pid, signal.SIGTERM)
                logger.info(f"Sent SIGTERM to process {pid}")
            except ProcessLookupError:
                logger.debug(f"Process {pid} not found")
            except Exception as e:
                logger.error(f"Error killing process {pid}: {e}")

        # Wait for processes to terminate
        time.sleep(1)

        # Force kill any remaining processes
        remaining_pids = find_service_pid()
        for pid in remaining_pids:
            try:
                os.kill(pid, signal.SIGKILL)
                logger.info(f"Sent SIGKILL to process {pid}")
            except ProcessLookupError:
                pass
            except Exception as e:
                logger.error(f"Error force killing process {pid}: {e}")

        # Clean up socket and lock files if they exist
        for file_path in [socket_path, lock_file]:
            if file_path.exists():
                try:
                    file_path.unlink()
                    logger.debug(f"Removed {file_path.name}")
                except Exception as e:
                    logger.error(f"Error removing {file_path.name}: {e}")

        # Try to remove runtime directory if empty
        try:
            if runtime_dir.exists() and not any(runtime_dir.iterdir()):
                runtime_dir.rmdir()
                logger.debug("Removed empty runtime directory")
        except Exception as e:
            logger.debug(f"Could not remove runtime directory: {e}")

        logger.info("Vector store service killed successfully")
    except Exception as e:
        logger.error(f"Error killing vector store service: {e}")
        raise Exception(
            f"Failed to kill vector store service: {str(e)}"
        ) from e
