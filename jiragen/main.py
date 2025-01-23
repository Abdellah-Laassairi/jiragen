"""Main entry point for jiragen CLI."""

import argparse
import sys
from pathlib import Path

import litellm
from rich.console import Console

from jiragen.cli.add import add_files_command
from jiragen.cli.clean import clean_command
from jiragen.cli.fetch import fetch_command
from jiragen.cli.generate import generate_issue
from jiragen.cli.init import init_command
from jiragen.cli.kill import kill_command
from jiragen.cli.restart import restart_command
from jiragen.cli.rm import rm_files_command
from jiragen.cli.status import status_command
from jiragen.cli.upload import upload_command
from jiragen.core.client import VectorStoreClient, VectorStoreConfig
from jiragen.core.config import ConfigManager
from jiragen.utils.data import get_data_dir, get_runtime_dir
from jiragen.utils.logger import logger, setup_logging

console = Console()


def get_vector_store() -> VectorStoreClient:
    """Get vector store instance with appropriate configuration."""
    runtime_dir = get_runtime_dir()
    store_config = VectorStoreConfig(
        collection_name="codebase_content",
        db_path=runtime_dir / "codebase_data" / "vector_db",
    )
    return VectorStoreClient(store_config)


def main():
    """Main entry point for the jiragen CLI."""
    try:
        parser = create_parser()
        args = parser.parse_args()

        # Setup logging based on verbosity
        log_file_path = get_data_dir() / "jiragen.log"
        setup_logging(args.verbose, log_file_path)
        litellm.set_verbose = args.verbose

        # Initialize config manager
        config_manager = ConfigManager()

        # Commands that don't need vector store
        if args.command == "init":
            init_command(args.config)
        elif args.command == "kill":
            kill_command()
        else:
            # Get vector store instance for commands that need it
            store = get_vector_store()

            # Dispatch to appropriate command
            if args.command == "add":
                add_files_command(
                    store, [str(f) for f in args.files]
                )  # Convert Path to str
            elif args.command == "rm":
                rm_files_command(
                    store, [str(f) for f in args.files]
                )  # Convert Path to str
            elif args.command == "clean":
                clean_command(store)
            elif args.command == "fetch":
                if not hasattr(args, "types") or args.types is None:
                    args.types = []
                query = getattr(args, "query", None)
                fetch_command(config_manager, query, args.types)
            elif args.command == "status":
                status_command(store, compact=args.compact)
            elif args.command == "restart":
                restart_command(
                    store=store
                )  # Pass the store instance to restart_command
            elif args.command == "generate":
                # Set default values if not provided
                template_path = args.template or str(
                    Path(__file__).parent / "templates" / "default.md"
                )
                # Generate ticket content and metadata
                result = generate_issue(
                    store=store,
                    message=args.message,
                    template_path=template_path,
                    model=args.model,
                    temperature=args.temperature,
                    max_tokens=args.max_tokens,
                    upload=args.upload,
                    yes=args.yes,
                )
                logger.success(
                    f"Issue generated successfully : {type(result)}"
                )

            elif args.command == "upload":
                upload_command(
                    title=args.title,
                    description=args.description,
                    issue_type=args.type,
                    epic_key=args.epic,
                    component_name=args.component,
                    priority=args.priority,
                    labels=args.labels,
                    assignee=args.assignee,
                    reporter=args.reporter,
                )
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/]")
        logger.exception("Unexpected error occurred")
        sys.exit(1)


def create_parser() -> argparse.ArgumentParser:
    """Create and return the command line argument parser."""
    # Create parent parser with common arguments
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose logging"
    )

    # Main parser
    parser = argparse.ArgumentParser(
        description="jiragen - AI-powered JIRA Issue generator",
        parents=[parent_parser],
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Init command
    init_parser = subparsers.add_parser(
        "init",
        help="Initialize jiragen in the current directory",
        parents=[parent_parser],
    )
    init_parser.add_argument(
        "-c",
        "--config",
        help="Path to config file",
        type=Path,
        default=None,
    )

    # Add command
    add_parser = subparsers.add_parser(
        "add",
        help="Add files to the vector store",
        parents=[parent_parser],
    )
    add_parser.add_argument("files", nargs="+", type=Path, help="Files to add")

    # Remove command
    rm_parser = subparsers.add_parser(
        "rm",
        help="Remove files from the vector store",
        parents=[parent_parser],
    )
    rm_parser.add_argument(
        "files", nargs="+", type=Path, help="Files to remove"
    )

    # Clean command
    clean_parser = subparsers.add_parser(
        "clean",
        help="Remove all files from the vector store",
        parents=[parent_parser],
    )

    # Fetch command
    fetch_parser = subparsers.add_parser(
        "fetch",
        help="Search for relevant code snippets",
        parents=[parent_parser],
    )
    fetch_parser.add_argument(
        "query",
        nargs="?",
        default=None,
        help="Search query. If not provided, fetches all data",
    )
    fetch_parser.add_argument(
        "--types",
        nargs="+",
        help="Filter by file types (e.g., epics, tickets, components). If not provided, fetches all types",
    )

    # Status command
    status_parser = subparsers.add_parser(
        "status",
        help="Show vector store status",
        parents=[parent_parser],
    )
    status_parser.add_argument(
        "-c", "--compact", action="store_true", help="Show compact status"
    )

    # Restart command
    restart_parser = subparsers.add_parser(
        "restart",
        help="Restart the vector store",
        parents=[parent_parser],
    )

    # Kill command
    kill_parser = subparsers.add_parser(
        "kill",
        help="Kill the vector store service",
        parents=[parent_parser],
    )

    # Generate command
    generate_parser = subparsers.add_parser(
        "generate",
        help="Generate a JIRA ticket",
        parents=[parent_parser],
    )
    generate_parser.add_argument(
        "message", help="Description of the ticket to generate"
    )
    generate_parser.add_argument(
        "-t", "--template", help="Path to template file"
    )
    generate_parser.add_argument("-m", "--model", help="LLM model to use")
    generate_parser.add_argument(
        "--temperature", type=float, help="Model temperature (0.0-1.0)"
    )
    generate_parser.add_argument(
        "--max-tokens", type=int, help="Maximum number of tokens to generate"
    )
    generate_parser.add_argument(
        "-e",
        "--editor",
        action="store_true",
        help="Open editor for manual editing",
    )
    generate_parser.add_argument(
        "-u",
        "--upload",
        action="store_true",
        help="Upload ticket after generation",
    )
    generate_parser.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="Skip all confirmations and use defaults",
    )

    # Upload command
    upload_parser = subparsers.add_parser(
        "upload",
        help="Upload a ticket to JIRA",
        parents=[parent_parser],
    )
    upload_parser.add_argument("title", help="Ticket title/summary")
    upload_parser.add_argument("description", help="Ticket description")
    upload_parser.add_argument(
        "-t", "--type", default="Story", help="Issue type (default: Story)"
    )
    upload_parser.add_argument("-e", "--epic", help="Epic key to link to")
    upload_parser.add_argument("-c", "--component", help="Component name")
    upload_parser.add_argument(
        "-p", "--priority", default="Medium", help="Priority (default: Medium)"
    )
    upload_parser.add_argument(
        "-l", "--labels", help="Comma-separated list of labels"
    )
    upload_parser.add_argument(
        "-a", "--assignee", help="Username to assign ticket to"
    )
    upload_parser.add_argument(
        "-r", "--reporter", help="Username to set as reporter"
    )

    return parser


if __name__ == "__main__":
    main()

# TODO : Fix component name and other metadata extraction
# TODO : fetch optimisation & fix bug
# TODO : Automatic title generation
# TODO : Global ignore pathspec rules
# TODO : performance optimization
# TODO : post-commit hook for issue generation
# TODO : Reranking optimization
