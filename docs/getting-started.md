# Getting Started

This guide will help you get up and running with JiraGen.

## Installation

First, install Jiragen using pip:

```bash
pip install jiragen
```

## Initial Setup

### Configuration

Run the initialization command to set up Jiragen:

```bash
jiragen init
```

This will:
1. Create the necessary directories following XDG Base Directory specification:
   - Configuration directory:
     - Linux/macOS: `~/.config/jiragen/`
     - Windows: `%APPDATA%\jiragen\`
   - Data directory:
     - Linux/macOS: `~/.local/share/jiragen/`
     - Windows: `%LOCALAPPDATA%\jiragen\`
2. Guide you through configuring:
   - JIRA connection settings
   - LLM preferences

You can accept the defaults by pressing Enter or customize each setting.

### Environment Variables

For automated setup, you can use environment variables:

```bash
# JIRA Settings
export JIRAGEN_URL="https://your-domain.atlassian.net"
export JIRAGEN_USERNAME="your-email@example.com"
export JIRAGEN_API_TOKEN="your-api-token"
export JIRAGEN_DEFAULT_PROJECT="PROJECT"
export JIRAGEN_DEFAULT_ASSIGNEE="username"

# LLM Settings
export JIRAGEN_LLM_MODEL="gpt-4"
export JIRAGEN_LLM_TEMPERATURE="0.7"
export JIRAGEN_LLM_MAX_TOKENS="2000"

# Optional: Custom paths
export XDG_CONFIG_HOME="~/.config"      # Unix-like systems
export XDG_DATA_HOME="~/.local/share"   # Unix-like systems
```

## Configuration

### 1. Initialize JiraGen

First, initialize JiraGen:

```bash
jiragen init
```

This will create the following directory structure following the XDG Base Directory specification:

**Unix-like Systems (Linux, macOS)**:
```
~/.config/jiragen/           # Configuration directory
├── config.ini              # Main configuration file
└── templates/             # Custom templates
    └── default.md

~/.local/share/jiragen/     # Data directory
├── vector_store/          # Vector database storage
├── jira_data/            # JIRA fetched data
│   ├── epics/           # Epic data
│   ├── tickets/         # Ticket data
│   └── components/      # Component data
└── jiragen.log          # Application logs
```

**Windows**:
```
%APPDATA%\jiragen\          # Configuration directory
├── config.ini              # Main configuration file
└── templates/             # Custom templates
    └── default.md

%LOCALAPPDATA%\jiragen\     # Data directory
├── vector_store/          # Vector database storage
├── jira_data/            # JIRA fetched data
│   ├── epics/           # Epic data
│   ├── tickets/         # Ticket data
│   └── components/      # Component data
└── jiragen.log          # Application logs
```

### 2. Configure JIRA Settings

Edit the configuration file (`~/.config/jiragen/config.ini` on Unix-like systems or `%APPDATA%\jiragen\config.ini` on Windows):

```ini
[jira]
url = https://your-domain.atlassian.net
username = your-email@example.com
api_token = your-api-token
default_project = PROJECT
default_assignee = username

[llm]
model = gpt-4
temperature = 0.7
max_tokens = 2000
```

You can also use environment variables:
```bash
export JIRA_URL=https://your-domain.atlassian.net
export JIRA_USERNAME=your-email@example.com
export JIRA_API_TOKEN=your-api-token
```

### 3. Add Your Codebase

Index your codebase to provide context for ticket generation:

```bash
jiragen add .
```

This will:
1. Scan your codebase recursively
2. Respect .gitignore patterns (skipping ignored files)
3. Create embeddings for relevant files
4. Store them in the vector store

You can also:
- Add specific files: `jiragen add src/main.py tests/test_api.py`
- Add a specific directory: `jiragen add src/`
- Add files matching a pattern: `jiragen add *.py`

The command will show:
- Progress bar during processing
- Tree view of added files
- Processing statistics (files/second)

Example output:
```
📁 Added Files
├── src/main.py
├── src/utils/helper.py
└── tests/test_api.py

Successfully added 3 files (52.7 files/second)
```

## Basic Usage

### Generate a Ticket

```bash
jiragen generate "Add dark mode support"
```

This will:
1. Search your staged jira data and codebase content for relevant context
2. Generate a detailed ticket description
3. Open it in your editor for review
4. Extract metadata (issue type, priority, labels)

### Generate and Upload

```bash
jiragen generate "Add dark mode support" --upload
```

This will:
1. Generate the ticket content
2. Show extracted metadata for review
3. Upload to JIRA after confirmation

### Automated Pipeline

```bash
jiragen generate "Add dark mode support" --upload --yes
```

This will:
1. Generate the ticket
2. Extract metadata
3. Upload to JIRA without confirmation

## Templates

### Default Template

JiraGen comes with a default template that structures tickets with:
- Description
- Acceptance Criteria
- Technical Details
- Implementation Notes

### Custom Templates

Create custom templates in the templates directory:
- Unix-like: `~/.config/jiragen/templates/`
- Windows: `%APPDATA%\jiragen\templates\`

```markdown
# {title}

## Description
{description}

## Implementation Plan
- [ ] Task 1
- [ ] Task 2

## Technical Requirements
{technical_details}

## Testing Strategy
- Unit Tests
- Integration Tests
- E2E Tests
```

Use your template:
```bash
jiragen generate "Feature request" --template custom.md
```

## Next Steps

- Check out the [CLI Reference](cli.md) for detailed command options
- Explore the [API Documentation](api/core.md) for programmatic usage
- Learn about [Contributing](https://github.com/Abdellah-Laassairi/jiragen/blob/main/CONTRIBUTING.md)
