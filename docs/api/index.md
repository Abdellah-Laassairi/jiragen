# API Reference

JiraGen provides a Python API for programmatic access to its functionality. This section covers the core modules and their usage.

## Core Modules

- `jiragen.core`: Core functionality and base classes
- `jiragen.services`: Integration services (JIRA, Vector Store)
- `jiragen.cli`: Command-line interface implementation
- `jiragen.utils`: Utility functions and helpers

## Basic Usage

```python
from jiragen import JiraGen
from jiragen.core import Generator
from jiragen.services import JiraClient

# Initialize JiraGen
jira_gen = JiraGen()

# Generate an issue
issue = jira_gen.generate(
    title="Add dark mode support", template="feature.md", model="gpt-4", temperature=0.7
)

# Upload to JIRA
issue_key = jira_gen.upload(issue)
print(f"Created issue: {issue_key}")
```

## Configuration

```python
from jiragen import Config

# Load configuration
config = Config.load()

# Update settings
config.jira.url = "https://your-domain.atlassian.net"
config.jira.username = "your-email@example.com"
config.jira.api_token = "your-api-token"

# Save changes
config.save()
```

## Vector Store Operations

```python
from jiragen.services import VectorStore

# Initialize vector store
store = VectorStore()

# Add files
store.add_files(["src/main.py", "tests/test_api.py"])

# Search for context
results = store.search("authentication implementation", limit=5)
```

See the following sections for detailed documentation on each module.
