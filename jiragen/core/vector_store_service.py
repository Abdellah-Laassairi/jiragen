import os
import pickle
import signal
import socket
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Dict

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from loguru import logger

SOCKET_TIMEOUT = 30  # 30 seconds timeout
BUFFER_SIZE = 16384  # 16KB buffer size


def setup_logging(log_path: Path):
    """Set up logging to both file and console"""
    log_format = "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {message}"
    log_file = log_path / "vector_store_service.log"
    logger.add(log_file, format=log_format, level="DEBUG", rotation="1 day")


class VectorStoreService:
    def __init__(self, socket_path: Path, runtime_dir: Path):
        self.socket_path = socket_path
        self.runtime_dir = runtime_dir
        self.running = False
        self.sock = None
        self.client = None
        self.collection = None
        self.embedding_function = None
        self.initialized = False
        self.db_path = None

        # Set up logging first
        setup_logging(runtime_dir)
        logger.info(f"Starting vector store service, PID: {os.getpid()}")

        self.runtime_dir.mkdir(parents=True, exist_ok=True)

        # Set up signal handlers
        signal.signal(signal.SIGTERM, self.handle_shutdown)
        signal.signal(signal.SIGINT, self.handle_shutdown)

    def initialize_store(self, config: Dict[str, Any]) -> None:
        """Initialize the vector store with the given configuration"""
        try:
            logger.debug("Starting store initialization")
            if self.initialized:
                logger.info("Store already initialized")
                return

            # Set up database path
            repo_path = Path(config["repo_path"])
            self.db_path = repo_path / ".jiragen" / "vector_store"
            self.db_path.mkdir(parents=True, exist_ok=True)

            # Initialize embedding function
            device = "cpu"  # Always use CPU for stability
            logger.debug(
                f"Initializing embedding function with device: {device}"
            )
            self.embedding_function = (
                embedding_functions.SentenceTransformerEmbeddingFunction(
                    model_name=config.get("model_name", "all-MiniLM-L6-v2"),
                    trust_remote_code=True,
                    device=device,
                )
            )

            # Initialize ChromaDB client
            logger.debug(f"Initializing ChromaDB client at {self.db_path}")
            self.client = chromadb.PersistentClient(
                path=str(self.db_path),
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True,
                    is_persistent=True,
                ),
            )

            # Get or create collection
            collection_name = config.get(
                "collection_name", "repository_content"
            )
            logger.debug(f"Getting/Creating collection: {collection_name}")
            try:
                self.collection = self.client.get_collection(
                    name=collection_name,
                    embedding_function=self.embedding_function,
                )
                logger.info(
                    f"Retrieved existing collection: {collection_name}"
                )
            except Exception as e:
                logger.warning(
                    f"Collection not found, creating a new one: {e}"
                )
                self.collection = self.client.create_collection(
                    name=collection_name,
                    embedding_function=self.embedding_function,
                )
                logger.info(f"Created new collection: {collection_name}")

            self.initialized = True
            logger.info("Vector store initialized successfully")

        except Exception as e:
            logger.exception("Failed to initialize store")
            raise RuntimeError("Failed to initialize vector store") from e

    def handle_add_files(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle adding files to the vector store"""
        logger.debug("Handling add_files")
        try:
            if not self.collection:
                return {"error": "Collection not initialized"}

            paths = [Path(p) for p in params["paths"]]
            added_files = set()

            for path in paths:
                if path.is_file():
                    try:
                        logger.debug(f"Reading file: {path}")
                        content = path.read_text()
                        file_id = str(path)

                        # Try to delete existing document first
                        try:
                            self.collection.delete(ids=[file_id])
                        except Exception as e:
                            logger.debug(
                                f"File not found in collection or error removing {path}: {e}"
                            )
                            pass

                        # Add the document
                        self.collection.add(
                            documents=[content],
                            metadatas=[{"file_path": str(path)}],
                            ids=[file_id],
                        )

                        added_files.add(str(path))
                        logger.debug(f"Successfully added file: {path}")

                    except Exception as e:
                        logger.error(f"Failed to add file {path}: {e}")

            return {"status": "success", "data": list(added_files)}

        except Exception as e:
            logger.exception("Failed to add files")
            raise RuntimeError("Failed to add files to vector store") from e

    def handle_remove_files(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle removing files from the vector store"""
        logger.debug("Handling remove_files")
        try:
            if not self.collection:
                return {"error": "Collection not initialized"}

            paths = [Path(p) for p in params["paths"]]
            removed_files = set()

            for path in paths:
                try:
                    file_id = str(path)
                    # Try to delete the document
                    try:
                        self.collection.delete(ids=[file_id])
                        removed_files.add(str(path))
                        logger.debug(f"Successfully removed file: {path}")
                    except Exception as e:
                        logger.debug(
                            f"File not found in collection or error removing {path}: {e}"
                        )

                except Exception as e:
                    logger.error(f"Failed to remove file {path}: {e}")

            return {"status": "success", "data": list(removed_files)}

        except Exception as e:
            logger.exception("Failed to remove files")
            raise RuntimeError(
                "Failed to remove files from vector store"
            ) from e

    def handle_get_stored_files(self) -> Dict[str, Any]:
        """Handle retrieving stored files information"""
        logger.debug("Handling get_stored_files")
        try:
            result = {"files": set(), "directories": set()}

            if not self.collection:
                logger.debug("No collection initialized")
                return {"status": "success", "data": result}

            try:
                start_time = time.time()
                # Get all documents metadata with timeout
                logger.debug("Getting all documents metadata")

                # Set a timeout for the get operation
                collection_data = None
                try:
                    with ThreadPoolExecutor(max_workers=1) as executor:
                        future = executor.submit(self.collection.get)
                        collection_data = future.result(
                            timeout=10
                        )  # 10 second timeout
                except TimeoutError:
                    logger.error("Timeout getting collection data")
                    return {"status": "success", "data": result}
                except Exception as e:
                    logger.error(f"Error getting collection data: {e}")
                    return {"status": "success", "data": result}

                if not collection_data:
                    logger.debug("No collection data found")
                    return {"status": "success", "data": result}

                all_metadata = collection_data.get("metadatas", [])
                logger.debug(f"Retrieved {len(all_metadata)} metadata entries")

                # Process metadata with timeout
                processed_count = 0

                file_paths = []
                for metadata in all_metadata:
                    if metadata and "file_path" in metadata:
                        file_paths.append(Path(metadata["file_path"]))

                for file_path in file_paths:
                    logger.debug(f"Processing file: {file_path}")
                    result["files"].add(str(file_path))
                    current_path = file_path.parent
                    while current_path != Path(".") and str(
                        current_path
                    ) != str(current_path.parent):
                        logger.debug(f"Inside while loop: {current_path}")
                        result["directories"].add(str(current_path))
                        current_path = current_path.parent

                    processed_count += 1

                duration = time.time() - start_time
                logger.debug(
                    f"Processed {processed_count} files in {duration:.2f} seconds"
                )
                return {"status": "success", "data": result}

            except Exception as e:
                logger.error(f"Error getting collection data: {e}")
                return {"status": "success", "data": result}

        except Exception as e:
            logger.exception("Error in get_stored_files")
            return {"error": str(e)}

    def handle_query_similar(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle querying similar documents"""
        try:
            if not self.collection:
                return {"status": "success", "data": []}

            text = params["text"]
            n_results = params.get("n_results", 5)

            results = self.collection.query(
                query_texts=[text], n_results=n_results
            )

            return {
                "status": "success",
                "data": [
                    {
                        "content": doc,
                        "metadata": meta,
                    }
                    for doc, meta in zip(
                        results["documents"][0],
                        results["metadatas"][0],
                        strict=False,
                    )
                ],
            }

        except Exception as e:
            logger.exception("Failed to query similar documents")
            raise RuntimeError("Failed to query similar documents") from e

    def handle_client(self, conn: socket.socket) -> None:
        """Handle a client connection"""
        try:
            # Set timeout for socket operations
            conn.settimeout(SOCKET_TIMEOUT)
            start_time = time.time()
            logger.debug("New client connection received")

            # Receive request data
            data = bytearray()
            while True:
                try:
                    chunk = conn.recv(BUFFER_SIZE)
                    if not chunk:
                        break
                    data.extend(chunk)

                    # Check for timeout
                    if time.time() - start_time > SOCKET_TIMEOUT:
                        raise TimeoutError("Operation timed out") from None
                except socket.timeout:
                    raise TimeoutError("Socket operation timed out") from None

            if not data:
                logger.warning("Empty request received")
                return

            # Process request
            request = pickle.loads(data)
            command = request.get("command")
            params = request.get("params", {})

            logger.debug(f"Processing command: {command}")

            # Handle commands
            if command == "ping":
                response = {"status": "success", "data": "pong"}
            elif command == "initialize":
                self.initialize_store(params)
                response = {"status": "success"}
            elif not self.initialized and command not in [
                "ping",
                "initialize",
            ]:
                response = {"error": "Service not initialized"}
            elif command == "get_stored_files":
                logger.debug("Recieved :  get_stored_files command")
                response = self.handle_get_stored_files()
            elif command == "add_files":
                response = self.handle_add_files(params)
            elif command == "remove_files":
                logger.debug("Recieved :  remove_files command")
                response = self.handle_remove_files(params)
            elif command == "query_similar":
                response = self.handle_query_similar(params)
            else:
                response = {"error": f"Unknown command: {command}"}

            # Send response
            serialized_response = pickle.dumps(response)
            conn.sendall(serialized_response)
            logger.debug(f"Response sent for command: {command}")

        except TimeoutError as e:
            logger.error(f"Timeout occurred: {e}")
            try:
                error_response = pickle.dumps({"error": "Operation timed out"})
                conn.sendall(error_response)
            except Exception as send_err:
                logger.error(f"Failed to send error response: {send_err}")
                pass
        except Exception as e:
            logger.exception("Error handling client request")
            try:
                error_response = pickle.dumps({"error": str(e)})
                conn.sendall(error_response)
            except Exception as send_err:
                logger.error(f"Failed to send error response: {send_err}")
                pass
        finally:
            try:
                conn.close()
                logger.debug("Connection closed")
            except Exception as e:
                logger.error(f"Error closing connection: {e}")
                pass

    def handle_shutdown(self, signum, frame) -> None:
        """Handle shutdown signal"""
        logger.info("Shutting down vector store service...")
        self.cleanup()
        sys.exit(0)

    def cleanup(self) -> None:
        """Clean up resources"""
        try:
            self.running = False
            if self.sock:
                self.sock.close()
            if self.socket_path.exists():
                self.socket_path.unlink()
            logger.info("Vector store service cleaned up")
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")

    def start(self) -> None:
        """Start the service"""
        try:
            # Remove existing socket file if it exists
            if self.socket_path.exists():
                self.socket_path.unlink()

            # Create and bind socket
            self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.sock.bind(str(self.socket_path))
            self.sock.listen(5)

            self.running = True
            logger.info(f"Vector store service started on {self.socket_path}")

            # Main service loop
            while self.running:
                try:
                    conn, _ = self.sock.accept()
                    # Handle each client in a separate thread
                    thread = threading.Thread(
                        target=self.handle_client, args=(conn,)
                    )
                    thread.daemon = True
                    thread.start()
                except OSError as e:
                    if self.running:
                        logger.error(f"Socket error occurred: {e}")
                    break
                except Exception as e:
                    logger.error(f"Error accepting connection: {e}")
                    continue

        except Exception as e:
            logger.exception(f"Failed to start service {str(e)}")
            self.cleanup()
            raise


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python vector_store_service.py <runtime_dir>")
        sys.exit(1)

    runtime_dir = Path(sys.argv[1])
    socket_path = runtime_dir / "vector_store.sock"

    service = VectorStoreService(socket_path, runtime_dir)
    service.start()


if __name__ == "__main__":
    main()
