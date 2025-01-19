import pickle
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Set

from loguru import logger
from pydantic import BaseModel, ConfigDict

MAX_RETRIES = 3
SOCKET_TIMEOUT = 15  # 15 seconds timeout
GET_FILES_TIMEOUT = 20  # 20 seconds for get_stored_files
BUFFER_SIZE = 16384  # 16KB buffer size


class VectorStoreConfig(BaseModel):
    repo_path: Path
    collection_name: str = "repository_content"
    embedding_model: str = "all-MiniLM-L6-v2"
    device: str = "cpu"  # Default to CPU for stability

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )


class VectorStoreClient:
    def __init__(self, config: VectorStoreConfig):
        self.config = config
        self.runtime_dir = Path.home() / ".jiragen"
        self.socket_path = self.runtime_dir / "vector_store.sock"
        self.ensure_service_running()
        self.initialize_store()

    def ensure_service_running(self) -> None:
        """Ensure the vector store service is running"""
        try:
            logger.debug("Checking if service is running...")
            if not self.socket_path.exists():
                logger.info("Starting vector store service...")
                self.start_service()
            else:
                try:
                    # Test connection with short timeout
                    self.send_command("ping", timeout=5)
                    logger.debug("Existing service responded to ping")
                except Exception as e:
                    logger.warning(
                        f"Existing service not responding ({e}), restarting..."
                    )
                    if self.socket_path.exists():
                        self.socket_path.unlink()
                    self.start_service()
        except Exception as e:
            logger.exception(f"Failed to ensure service is running {str(e)}")
            raise

    def start_service(self) -> None:
        """Start the vector store service"""
        try:
            service_script = Path(__file__).parent / "vector_store_service.py"
            if not service_script.exists():
                raise FileNotFoundError(
                    f"Service script not found at {service_script}"
                )

            logger.debug(f"Starting service from script: {service_script}")
            self.runtime_dir.mkdir(parents=True, exist_ok=True)

            # Start service process
            python_path = sys.executable
            process = subprocess.Popen(
                [python_path, str(service_script), str(self.runtime_dir)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True,
            )

            # Wait for socket file to appear
            start_time = time.time()
            while not self.socket_path.exists():
                if time.time() - start_time > SOCKET_TIMEOUT:
                    stdout, stderr = process.communicate()
                    logger.error(f"Service stdout: {stdout.decode()}")
                    logger.error(f"Service stderr: {stderr.decode()}")
                    raise TimeoutError("Service failed to start")
                time.sleep(0.1)

            # Wait for service to initialize
            time.sleep(2)

            # Verify service is responding
            retries = 3
            while retries > 0:
                try:
                    self.send_command("ping", timeout=5)
                    logger.info("Service started successfully")
                    return
                except Exception as e:
                    logger.warning(
                        f"Service not responding, retrying... ({str(e)})"
                    )
                    retries -= 1
                    if retries == 0:
                        raise
                    time.sleep(1)

        except Exception as e:
            logger.exception(f"Failed to start service {str(e)}")
            raise

    def restart(self) -> None:
        """Restart the vector store service."""
        try:
            config = {
                "repo_path": str(self.config.repo_path),
                "collection_name": self.config.collection_name,
                "model_name": self.config.embedding_model,
            }
            self.send_command("restart", params=config)
        except Exception as e:
            logger.exception("Failed to restart vector store service")
            raise Exception(
                f"Failed to restart vector store service: {str(e)}"
            ) from e

    def kill(self) -> None:
        """Kill the vector store service."""
        try:
            self.send_command("kill")
        except Exception as e:
            logger.exception("Failed to kill vector store service")
            raise Exception(
                f"Failed to kill vector store service: {str(e)}"
            ) from e

    def send_command(
        self,
        command: str,
        params: Dict[str, Any] = None,
        timeout: int = SOCKET_TIMEOUT,
        retries: int = MAX_RETRIES,
    ) -> Dict[str, Any]:
        """Send command to service with retries"""
        if params is None:
            params = {}

        last_error = None
        while retries > 0:
            sock = None
            try:
                # Create new socket for each attempt
                sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                sock.settimeout(timeout)  # Set timeout for all operations
                sock.connect(str(self.socket_path))

                # Send request
                request = {"command": command, "params": params}
                msg = pickle.dumps(request)
                sock.sendall(msg)
                sock.shutdown(socket.SHUT_WR)  # Signal end of sending

                # Read response
                data = bytearray()
                while True:
                    try:
                        chunk = sock.recv(BUFFER_SIZE)
                        if not chunk:
                            break
                        data.extend(chunk)
                    except socket.timeout as e:
                        logger.error(f"Failed to receive data: {e}")
                        raise TimeoutError(
                            f"Timeout while receiving data for command: {command}"
                        ) from e

                if not data:
                    raise ConnectionError("Empty response from service")

                response = pickle.loads(data)
                if "error" in response:
                    raise Exception(response["error"])

                return response

            except Exception as e:
                last_error = e
                retries -= 1
                if retries > 0:
                    logger.warning(
                        f"Command {command} failed, retrying... ({e})"
                    )
                    time.sleep(1)
                else:
                    logger.error(
                        f"Command {command} failed after all retries: {e}"
                    )
                    raise Exception(
                        f"Command {command} failed after all retries: {e}"
                    ) from last_error
            finally:
                if sock:
                    try:
                        sock.close()
                    except Exception as e:
                        logger.warning(f"Failed to close socket: {e}")
                        pass

    def initialize_store(self) -> None:
        """Initialize the vector store with initialization state verification.

        The initialization process:
        1. Send initialize command with config
        2. Verify store accessibility through get_stored_files
        3. Confirm data structure integrity
        """
        try:
            config_dict = {
                "repo_path": str(self.config.repo_path),
                "collection_name": self.config.collection_name,
                "embedding_model": self.config.embedding_model,
                "device": self.config.device,
            }

            # Send initialization command
            response = self.send_command("initialize", config_dict)
            if response.get("status") != "success":
                raise Exception(
                    f"Failed to initialize store: {response.get('error', 'Unknown error')}"
                )

            # Verify store accessibility
            retry_count = 3
            while retry_count > 0:
                try:
                    test_response = self.send_command(
                        "get_stored_files", timeout=5
                    )
                    if (
                        isinstance(test_response, dict)
                        and "data" in test_response
                    ):
                        data = test_response["data"]
                        if (
                            isinstance(data, dict)
                            and "files" in data
                            and "directories" in data
                        ):
                            logger.info(
                                "Vector store initialized and verified successfully"
                            )
                            return
                except Exception as e:
                    logger.debug(
                        f"Initialization verification attempt {4-retry_count}/3 failed: {e}"
                    )

                retry_count -= 1
                if retry_count > 0:
                    time.sleep(1)

            raise Exception(
                "Failed to verify store initialization state after retries"
            )

        except Exception as e:
            logger.exception(f"Failed to initialize store {str(e)}")
            raise

    def get_stored_files(self) -> Dict[str, Set[Path]]:
        """Get stored files with robust validation and error handling.

        Returns:
            Dict[str, Set[Path]]: Dictionary containing:
                - 'files': Set of file paths
                - 'directories': Set of directory paths
        """
        try:
            response = self.send_command(
                "get_stored_files", timeout=GET_FILES_TIMEOUT
            )

            # Validate response structure
            if not isinstance(response, dict):
                logger.error(f"Invalid response type: {type(response)}")
                return {"files": set(), "directories": set()}

            if "data" not in response:
                logger.error("Response missing 'data' field")
                return {"files": set(), "directories": set()}

            data = response["data"]
            if not isinstance(data, dict):
                logger.error(f"Invalid data structure type: {type(data)}")
                return {"files": set(), "directories": set()}

            # Convert paths with error handling
            try:
                files = {
                    Path(p)
                    for p in data.get("files", set())
                    if p and isinstance(p, (str, Path))
                }
                directories = {
                    Path(p)
                    for p in data.get("directories", set())
                    if p and isinstance(p, (str, Path))
                }
            except (TypeError, ValueError) as e:
                logger.error(f"Path conversion error: {e}")
                return {"files": set(), "directories": set()}

            return {"files": files, "directories": directories}

        except Exception as e:
            logger.exception(f"Failed to get stored files {str(e)}")
            return {"files": set(), "directories": set()}

    def add_files(self, paths: List[Path]) -> Set[Path]:
        """Add files to vector store"""
        try:
            # logger.debug(f"Adding files: {paths}")
            response = self.send_command(
                "add_files", {"paths": [str(p) for p in paths]}, timeout=60
            )  # Longer timeout for file operations

            if not response or "data" not in response:
                raise Exception("Invalid response from service")

            added_files = {Path(p) for p in response["data"]}
            logger.info(f"Successfully added {len(added_files)} files")
            return added_files

        except Exception as e:
            logger.exception("Failed to add files")
            raise Exception(f"Failed to add files: {str(e)}") from e

    def remove_files(self, paths: List[Path]) -> Set[Path]:
        """Remove files from vector store"""
        try:
            response = self.send_command(
                "remove_files", {"paths": [str(p) for p in paths]}, timeout=60
            )  # Longer timeout for file operations

            if not response or "data" not in response:
                raise Exception("Invalid response from service")

            removed_files = {Path(p) for p in response["data"]}
            logger.info(f"Successfully removed {len(removed_files)} files")
            return removed_files

        except Exception as e:
            logger.exception("Failed to remove files")
            raise Exception(f"Failed to remove files: {str(e)}") from e

    def query_similar(
        self, text: str, n_results: int = 5
    ) -> List[Dict[str, Any]]:
        """Query similar documents"""
        try:
            response = self.send_command(
                "query_similar",
                {"text": text, "n_results": n_results},
                timeout=60,
            )  # Longer timeout for query operations

            if not response or "data" not in response:
                raise Exception("Invalid response from service")
            return response["data"]
        except Exception as e:
            logger.exception(f"Failed to query similar documents {str(e)}")
            return []
