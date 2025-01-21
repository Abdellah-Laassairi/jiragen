# Core API Reference

This section documents the core components of JiraGen. These components form the foundation of the application and provide essential functionality for ticket generation, metadata handling, and JIRA integration.

## Vector Store

!!! abstract "Overview"
    The Vector Store module handles the storage and retrieval of code embeddings, enabling semantic search over your codebase.

### VectorStoreConfig

::: jiragen.core.client.VectorStoreConfig
    rendering:
      show_root_heading: true
      show_source: false

### VectorStoreClient

::: jiragen.core.client.VectorStoreClient
    rendering:
      show_root_heading: true
      show_source: false

### VectorStoreService

::: jiragen.services.vector_store.VectorStoreService
    rendering:
      show_root_heading: true
      show_source: false

## Generator

!!! abstract "Overview"
    The Generator module is responsible for generating ticket content using AI models and managing the generation process.

### LLMConfig

::: jiragen.core.generator.LLMConfig
    rendering:
      show_root_heading: true
      show_source: false

### LiteLLMClient

::: jiragen.core.generator.LiteLLMClient
    rendering:
      show_root_heading: true
      show_source: false

### IssueGenerator

::: jiragen.core.generator.IssueGenerator
    rendering:
      show_root_heading: true
      show_source: false

## Metadata

!!! abstract "Overview"
    The Metadata module handles JIRA issue metadata, including issue types, priorities, and field validation.

!!! example "Usage Example"
    ```python
    from jiragen.core.metadata import IssueMetadata, IssueType, IssuePriority

    # Create metadata for a new feature
    metadata = IssueMetadata(
        issue_type=IssueType.STORY,
        priority=IssuePriority.HIGH,
        labels=["feature", "ui"],
        components=["frontend"],
        story_points=5,
    )
    ```

### IssueType

::: jiragen.core.metadata.IssueType
    rendering:
      show_root_heading: true
      show_source: false

### IssuePriority

::: jiragen.core.metadata.IssuePriority
    rendering:
      show_root_heading: true
      show_source: false

### IssueMetadata

::: jiragen.core.metadata.IssueMetadata
    rendering:
      show_root_heading: true
      show_source: false

### IssueMetadataExtractor

::: jiragen.core.metadata.IssueMetadataExtractor
    rendering:
      show_root_heading: true
      show_source: false

## Config

!!! abstract "Overview"
    The Config module manages application configuration, including JIRA credentials and default settings.

!!! tip "Environment Variables"
    Configuration can also be set using environment variables:
    ```bash
    export JIRA_URL=https://your-domain.atlassian.net
    export JIRA_USERNAME=your-email@example.com
    export JIRA_API_TOKEN=your-api-token
    ```

### ConfigManager

::: jiragen.core.config.ConfigManager
    rendering:
      show_root_heading: true
      show_source: false
