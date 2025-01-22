# Core API

The core module provides the fundamental functionality of JiraGen.

## JiraGen Class

The main class that orchestrates all functionality.

```python
from jiragen import JiraGen


class JiraGen:
    def __init__(self, config_path: Optional[str] = None):
        """Initialize JiraGen with optional custom config path."""

    def generate(
        self,
        title: str,
        template: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> Issue:
        """Generate a JIRA issue with AI assistance."""

    def upload(self, issue: Issue) -> str:
        """Upload an issue to JIRA and return the issue key."""

    def add_files(self, paths: List[str]) -> int:
        """Add files to the vector store."""
```

## Generator Class

Handles AI-powered issue generation.

```python
from jiragen.core import Generator


class Generator:
    def __init__(
        self, model: str = "gpt-4", temperature: float = 0.7, max_tokens: int = 2000
    ):
        """Initialize the generator with model settings."""

    def generate(
        self, title: str, context: List[str], template: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate issue content using AI."""
```

## Issue Class

Represents a JIRA issue with all its metadata.

```python
from jiragen.core import Issue


class Issue:
    def __init__(
        self,
        title: str,
        description: str,
        issue_type: str = "Story",
        priority: Optional[str] = None,
        labels: Optional[List[str]] = None,
        components: Optional[List[str]] = None,
    ):
        """Initialize an issue with its metadata."""

    def to_dict(self) -> Dict[str, Any]:
        """Convert issue to JIRA API format."""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Issue":
        """Create issue from JIRA API response."""
```

## Config Class

Manages application configuration.

```python
from jiragen.core import Config


class Config:
    @classmethod
    def load(cls, path: Optional[str] = None) -> "Config":
        """Load configuration from file."""

    def save(self, path: Optional[str] = None) -> None:
        """Save configuration to file."""

    @property
    def jira(self) -> JiraConfig:
        """Get JIRA configuration section."""

    @property
    def llm(self) -> LLMConfig:
        """Get LLM configuration section."""
```

## Exceptions

Custom exceptions for error handling.

```python
from jiragen.core.exceptions import (
    JiraGenError,
    ConfigError,
    JiraError,
    GenerationError,
    VectorStoreError,
)


class JiraGenError(Exception):
    """Base exception for all JiraGen errors."""


class ConfigError(JiraGenError):
    """Configuration related errors."""


class JiraError(JiraGenError):
    """JIRA API related errors."""


class GenerationError(JiraGenError):
    """AI generation related errors."""


class VectorStoreError(JiraGenError):
    """Vector store related errors."""
```

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
