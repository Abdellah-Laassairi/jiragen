"""Generate JIRA ticket content and metadata using AI."""

import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from loguru import logger
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt

from jiragen.cli.nvim import open_in_neovim, setup_nvim_environment
from jiragen.cli.upload import upload_command
from jiragen.core.client import VectorStoreClient
from jiragen.core.generator import GeneratorConfig, IssueGenerator, LLMConfig
from jiragen.core.metadata import (
    IssueMetadata,
    IssueMetadataExtractor,
    IssuePriority,
    IssueType,
)

console = Console()


def _setup_generator(
    store: VectorStoreClient,
    template_path: str,
    model: str,
    temperature: float,
    max_tokens: int,
) -> tuple[GeneratorConfig, IssueGenerator, LLMConfig]:
    """Set up the generator with the given configuration."""
    template = Path(template_path)
    if not template.exists():
        raise FileNotFoundError(f"Template file not found: {template}")

    console.print("[bold]Setting up generator...[/]")
    llm_config = LLMConfig(
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    config = GeneratorConfig(template_path=template, llm_config=llm_config)
    generator = IssueGenerator(store, config)
    return config, generator, llm_config


def _generate_and_edit_content(
    generator: IssueGenerator, message: str, yes: bool
) -> Optional[str]:
    """Generate issue content and optionally edit it."""
    console.print("[bold]Generating issue content...[/]")
    issue_content = generator.generate(message)
    console.print("[green]✓[/] Issue generated successfully!")

    # Open in Neovim for editing if requested and not in auto mode
    if not yes:
        modified_content = open_in_neovim(issue_content)
        if modified_content is None:
            console.print("[yellow]Issue editing was cancelled[/]")
            return None
    else:
        modified_content = issue_content

    # Display the final issue content
    console.print(
        Panel(
            modified_content,
            title="[bold green]Generated JIRA Issue Content[/]",
            border_style="green",
        )
    )
    return modified_content


def _extract_and_display_metadata(
    content: str, llm_config: LLMConfig
) -> IssueMetadata:
    """Extract and display issue metadata."""
    console.print("[bold]Analyzing issue metadata...[/]")
    extractor = IssueMetadataExtractor(llm_config)
    metadata_json = extractor.extract_metadata(content)
    logger.info(f"Successfully extracted metadata: {metadata_json}")

    # Parse metadata from JSON string to IssueMetadata object
    if isinstance(metadata_json, str):
        metadata_dict = json.loads(metadata_json)
        metadata = IssueMetadata(**metadata_dict)
    else:
        metadata = metadata_json

    # Set the description field
    metadata.description = content

    # Display metadata in a nice format
    console.print("\n[bold]Generated Metadata:[/]")
    console.print(f"Issue Type: {metadata.issue_type}")
    console.print(f"Priority: {metadata.priority}")
    console.print(f"Labels: {', '.join(metadata.labels)}")
    console.print(f"Story Points: {metadata.story_points}")
    console.print(f"Components: {', '.join(metadata.components)}")

    return metadata


def _modify_metadata(metadata: IssueMetadata) -> IssueMetadata:
    """Allow user to modify metadata interactively."""
    metadata.issue_type = Prompt.ask(
        "Issue Type",
        choices=[t.value for t in IssueType],
        default=str(metadata.issue_type),
    )
    metadata.priority = Prompt.ask(
        "Priority",
        choices=[p.value for p in IssuePriority],
        default=str(metadata.priority),
    )
    labels_str = Prompt.ask(
        "Labels (comma-separated)",
        default=",".join(metadata.labels) if metadata.labels else "",
    )
    metadata.labels = [
        label.strip() for label in labels_str.split(",") if label.strip()
    ]

    components_str = Prompt.ask(
        "Components (comma-separated)",
        default=",".join(metadata.components) if metadata.components else "",
    )
    metadata.components = [
        comp.strip() for comp in components_str.split(",") if comp.strip()
    ]

    story_points = Prompt.ask(
        "Story Points (1-13, Fibonacci)",
        default=str(metadata.story_points) if metadata.story_points else "",
    )
    metadata.story_points = (
        int(story_points) if story_points.isdigit() else None
    )

    return metadata


def _upload_to_jira(
    content: str, metadata: IssueMetadata, message: str
) -> Optional[str]:
    """Upload the issue to JIRA."""
    try:
        issue_key = upload_command(
            title=message,  # Using the original message as title
            description=content,
            issue_type=metadata.issue_type,
            priority=metadata.priority,
            labels=",".join(metadata.labels),
            component_name=metadata.components[0]
            if metadata.components
            else None,
        )
        if issue_key:
            console.print(
                f"\n[green]✓[/] Issue uploaded successfully! Key: {issue_key}"
            )
            return issue_key
        else:
            console.print("\n[red]Failed to upload issue[/]")
            return None
    except Exception as e:
        console.print(f"[red]Error uploading issue: {str(e)}[/]")
        return None


def generate_issue(
    store: VectorStoreClient,
    message: str,
    template_path: str,
    model: str = "openai/gpt-4o",
    temperature: float = 0.7,
    max_tokens: int = 2000,
    upload: bool = False,
    yes: bool = False,
) -> Optional[Dict[str, Any]]:
    """Generate JIRA issue content and metadata using AI."""
    try:
        # Check Neovim environment
        setup_nvim_environment()

        # Set up the generator
        config, generator, llm_config = _setup_generator(
            store, template_path, model, temperature, max_tokens
        )

        # Generate and edit content
        content = _generate_and_edit_content(generator, message, yes)
        if content is None:
            return None

        # Extract and process metadata
        metadata = _extract_and_display_metadata(content, llm_config)

        if upload:
            # Allow user to modify metadata if not in auto mode
            if not yes and Confirm.ask(
                "\nWould you like to modify the metadata?", default=False
            ):
                metadata = _modify_metadata(metadata)

            # Upload to JIRA (auto-confirm if yes flag is set)
            if yes or Confirm.ask(
                "\nDo you want to upload this issue to JIRA?", default=True
            ):
                _upload_to_jira(content, metadata, message)

        return metadata

    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/]")
        sys.exit(1)
