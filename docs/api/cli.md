# CLI API Reference

This section documents the command-line interface components of JiraGen. These components provide the user-facing functionality for ticket generation, metadata handling, and JIRA integration.

## Generate Command

!!! abstract "Overview"
    The Generate command creates JIRA tickets using AI, with support for interactive editing and metadata modification.

!!! example "Usage Example"
    ```python
    from jiragen.cli.generate import generate_issue
    from jiragen.core.vector_store import VectorStoreClient

    # Initialize vector store
    store = VectorStoreClient()

    # Generate a ticket
    result = generate_issue(
        store=store,
        message="Add dark mode support",
        model="openai/gpt-4o",
        upload=True,
        yes=False,  # Enable interactive mode
    )
    ```

### generate_issue

::: jiragen.cli.generate.generate_issue
    rendering:
      show_root_heading: true
      show_source: false

### open_in_neovim

!!! tip "Editor Integration"
    The `open_in_neovim` function provides seamless integration with Neovim for content editing. Make sure Neovim is installed and configured properly.

::: jiragen.cli.nvim.open_in_neovim
    rendering:
      show_root_heading: true
      show_source: false

## Add Command

!!! abstract "Overview"
    The Add command indexes your codebase into the vector store for context-aware ticket generation.

!!! warning "Large Codebases"
    For large codebases, the indexing process may take some time. The command shows a progress bar and provides detailed statistics upon completion.

### add_files_command

::: jiragen.cli.add.add_files_command
    rendering:
      show_root_heading: true
      show_source: false

## Init Command

!!! abstract "Overview"
    The Init command sets up JiraGen's configuration and creates necessary directories.

!!! tip "Configuration"
    The init process will:
    1. Create the `.jiragen` directory
    2. Initialize the configuration file
    3. Set up the vector store
    4. Configure JIRA credentials

### init_command

::: jiragen.cli.init.init_command
    rendering:
      show_root_heading: true
      show_source: false

## Upload Command

!!! abstract "Overview"
    The Upload command handles the creation of JIRA issues with proper metadata and content formatting.

!!! example "Usage Example"
    ```python
    from jiragen.cli.upload import upload_command

    # Upload a new feature request
    issue_key = upload_command(
        title="Add Dark Mode Support",
        description="# Feature Request\n\nImplement dark mode...",
        issue_type="Story",
        priority="High",
        labels="frontend,ui,dark-mode",
        component_name="UI",
    )
    print(f"Created issue: {issue_key}")
    ```

### upload_command

::: jiragen.cli.upload.upload_command
    rendering:
      show_root_heading: true
      show_source: false

### JIRA Integration Utilities

!!! note "Helper Functions"
    The following functions help validate and format data for JIRA:

### read_config

::: jiragen.cli.upload.read_config
    rendering:
      show_root_heading: true
      show_source: false

### get_project_key

::: jiragen.cli.upload.get_project_key
    rendering:
      show_root_heading: true
      show_source: false

### validate_component

::: jiragen.cli.upload.validate_component
    rendering:
      show_root_heading: true
      show_source: false

### validate_epic

::: jiragen.cli.upload.validate_epic
    rendering:
      show_root_heading: true
      show_source: false

### validate_priority

::: jiragen.cli.upload.validate_priority
    rendering:
      show_root_heading: true
      show_source: false

### validate_labels

::: jiragen.cli.upload.validate_labels
    rendering:
      show_root_heading: true
      show_source: false

### convert_md_to_jira

::: jiragen.cli.upload.convert_md_to_jira
    rendering:
      show_root_heading: true
      show_source: false
