# Configuration

This document outlines the configuration settings and directory structure for the Jiragen project.

## Directory Structure

Jiragen follows the XDG Base Directory specification for storing configuration and data files:

### Unix-like Systems (Linux, macOS)

```
~/.config/jiragen/           # Configuration directory
└── config.ini              # Main configuration file

~/.local/share/jiragen/     # Data directory
├── vector_store/          # Vector database storage
└── jiragen.log           # Application logs
```

### Windows

```
%APPDATA%\jiragen\          # Configuration directory
└── config.ini              # Main configuration file

%LOCALAPPDATA%\jiragen\     # Data directory
├── vector_store/          # Vector database storage
└── jiragen.log           # Application logs
```

## Configuration File

The `config.ini` file contains three main sections:

### JIRA Configuration
```ini
[JIRA]
url = https://your-domain.atlassian.net
username = your-email@example.com
api_token = your-api-token
default_project = PROJECT
default_assignee = username
```

### LLM Configuration
```ini
[llm]
model = openai/gpt-4o
temperature = 0.7
max_tokens = 2000
```

### Vector Store Configuration
```ini
[vector_store]
path = ~/.local/share/jiragen/vector_store  # Automatically set based on OS
```

## Environment Variables

You can configure Jiragen using environment variables:

### JIRA Settings
- `JIRAGEN_URL`: The URL of the JIRA instance
- `JIRAGEN_USERNAME`: The username for JIRA authentication
- `JIRAGEN_API_TOKEN`: The API token for accessing JIRA
- `JIRAGEN_DEFAULT_PROJECT`: The default project key in JIRA
- `JIRAGEN_DEFAULT_ASSIGNEE`: The default assignee for created issues

### LLM Settings
- `JIRAGEN_LLM_MODEL`: The LLM model to use
- `JIRAGEN_LLM_TEMPERATURE`: Temperature setting for the LLM
- `JIRAGEN_LLM_MAX_TOKENS`: Maximum tokens for LLM responses

### Vector Store Settings
- `JIRAGEN_VECTOR_STORE_PATH`: Custom path for vector store data

### Directory Overrides
- `XDG_CONFIG_HOME`: Override default config directory (Unix-like systems)
- `XDG_DATA_HOME`: Override default data directory (Unix-like systems)
- `APPDATA`: Override config directory (Windows)
- `LOCALAPPDATA`: Override data directory (Windows)

## Configuration Precedence

The configuration values are loaded in the following order (later values override earlier ones):

1. Default values
2. Values from config file
3. Environment variables
4. Command-line arguments (when applicable)

## Initialization

When running `jiragen init`, you'll be prompted to configure all sections. You can:
- Enter values manually
- Press Enter to accept defaults
- Use environment variables to pre-populate values

Example:
```bash
$ jiragen init

JIRA Configuration:
JIRA URL (e.g., https://your-domain.atlassian.net):
Username (usually your email):
API Token:
Default Project Key:
Default Assignee:

LLM Configuration:
Model name (default: openai/gpt-4o):
Temperature (0.0-1.0, default: 0.7):
Maximum tokens (default: 2000):

Vector Store Configuration:
Vector store path (default: ~/.local/share/jiragen/vector_store):
```

Ensure that all configuration settings are properly documented and up-to-date.
