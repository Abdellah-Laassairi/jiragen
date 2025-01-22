# CLI Reference

```bash
jiragen [command] [options] [arguments]
```

## Global Options

- `--verbose`: Enable detailed logging
- `--config PATH`: Specify custom config file location
- `--help`: Display command help

## Commands

### init

Initialize JiraGen configuration and create necessary directories.

```bash
jiragen init
```

This command will initialize the configuration file.

### generate

Generate JIRA tickets using AI with context from your codebase.

```bash
jiragen generate MESSAGE [OPTIONS]

Arguments:
  MESSAGE              : Description of the ticket to generate

Options:
  -t, --template PATH : Path to template file (default: bundled default.md)
  -m, --model NAME    : LLM model to use (default: openai/gpt-4o)
  --temperature FLOAT : Model temperature (0.0-1.0) (default: 0.7)
  --max-tokens INT    : Maximum number of tokens to generate (default: 2000)
  -e, --editor       : Open editor for manual editing
  -u, --upload       : Upload ticket to JIRA after generation
  -y, --yes          : Skip all confirmations and use defaults
```

The generate command now supports an interactive workflow:

1. **Content Generation**:
   - Generates ticket content using AI
   - Opens in editor for manual modifications (unless `-y` is used)
   - Displays the final content

2. **Metadata Extraction**:
   - Automatically extracts metadata like issue type, priority, labels
   - Shows extracted metadata for review
   - Allows interactive modification (unless `-y` is used)

3. **JIRA Upload** (with `-u` flag):
   - Confirms before upload (unless `-y` is used)
   - Validates components and other fields
   - Shows upload status and issue link

Example usage:

```bash
# Generate ticket with default settings
jiragen generate "Add user authentication feature"

# Generate and upload to JIRA with confirmation
jiragen generate "Implement OAuth2" --upload

# Generate and upload with custom model, skipping all confirmations
jiragen generate "Fix memory leak" --model openai/gpt-4 --upload --yes

# Generate with custom template and manual editing
jiragen generate "Add dark mode" --template feature.md --editor
```

Interactive metadata editing example:
```
Generated Metadata:
Issue Type: Task
Priority: High
Labels: frontend, UI, dark-mode
Story Points: 5
Components: UI

Would you like to modify the metadata? [y/N]:
```

Upload confirmation example:
```
Do you want to upload this issue to JIRA? [Y/n]:
✓ Successfully created Jira issue: https://your-domain.atlassian.net/browse/PROJ-123
```

### fetch

Fetch JIRA data and store it in a separate vector store. The command will display a progress bar while fetching and show detailed statistics upon completion.

```bash
jiragen fetch [OPTIONS]

Options:
  --types TYPE [TYPE...]  : Types of data to fetch (default: tickets, epics)
                           Available types: epics, tickets, components
                           Use 'all' to fetch everything
```

Example usage:

```bash
# Fetch all JIRA data types
jiragen fetch --types all

# Fetch specific types
jiragen fetch --types epics tickets
```

Output example:

```
    JIRA Fetch Statistics
┏━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┓
┃ Type       ┃ Items Fetched ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━━━━━━┩
│ Epics      │            12 │
│ Tickets    │           156 │
│ Components │             8 │
│ Total      │           176 │
└────────────┴───────────────┘

┌─────────── Summary ───────────────┐
│                                  │
│ ✨ Fetch completed successfully!  │
│ ⏱️  Time taken: 5.23 seconds      │
│ 📁 Data stored in: .jiragen/jira_data │
│                                  │
└──────────────────────────────────┘
```

The fetched data is stored in the runtime directory followed by `jira_data`, organized by type:

- `jira_data/epics/`
- `jira_data/tickets/`
- `jira_data/components/`

Each item is stored in both JSON and Markdown formats for easy viewing and processing.

### status

Display status of files in the vector store database.

```bash
jiragen status [OPTIONS]

Options:
  --compact           : Show compact view with file counts
  --depth INT        : Maximum depth of directory tree to display
```

### add

Add files to the vector store database. Supports .gitignore patterns and recursive directory scanning.

```bash
jiragen add PATH [PATH...]

Arguments:
  PATH               : One or more files or directories to add to the database
                      Use "." to add all files in current directory recursively
                      Use "*" to add all files in current directory only
                      Use specific paths for individual files or directories

Examples:
# Add all files recursively (respects .gitignore)
jiragen add .

# Add specific files
jiragen add src/main.py tests/test_api.py

# Add all files in a specific directory
jiragen add src/

# Add all Python files in current directory
jiragen add *.py
```

The command will:
1. Respect .gitignore patterns when scanning for files
2. Show a progress bar during processing
3. Display a tree view of added files
4. Show processing statistics (files/second)
5. Skip directories and only process files

Output example:
```
📁 Added Files
├── src/main.py
├── src/utils/helper.py
└── tests/test_api.py

Successfully added 3 files (52.7 files/second)
```

### rm (remove)

Remove files from the vector store database.

```bash
jiragen rm PATH [PATH...]

Arguments:
  PATH               : One or more files to remove from the database
```

### restart

Restart the vector store service. Useful when you need to reset the database connection.

```bash
jiragen restart
```

### upload

Upload Jira issues directly from the command line. Supports all issue types (Story, Bug, Task, Epic, etc.) and includes markdown to Jira markup conversion.

```bash
jiragen upload [OPTIONS]

Required Options:
  --title TEXT       : Issue title/summary

Optional Options:
  --description TEXT : Issue description (supports markdown format)
  --type TEXT       : Issue type (Story, Bug, Task, Epic, etc.) (default: Story)
  --epic KEY        : Epic key to link the issue to (e.g., ODT-123)
  --component TEXT  : Component name to assign
  --priority TEXT   : Priority level (Highest, High, Medium, Low, Lowest)
  --labels TEXT     : Comma-separated list of labels
  --assignee TEXT   : Username of the assignee
  --reporter TEXT   : Username of the reporter
```

Example usage:

```bash
# Create a basic story
jiragen upload --title "Implement user authentication"

# Create a high-priority bug with labels
jiragen upload \
  --title "Fix login page crash" \
  --type Bug \
  --priority High \
  --labels "bug,urgent" \
  --assignee "john.doe"

# Create an epic with markdown description
jiragen upload \
  --title "Q1 Feature Set" \
  --type Epic \
  --description "# Q1 Features\n\n## Goals\n- Implement OAuth\n- Add user profiles\n\n## Timeline\n1. January: Planning\n2. February: Development\n3. March: Testing"

# Create a story linked to an epic
jiragen upload \
  --title "Add OAuth integration" \
  --description "## Overview\nImplement OAuth2 authentication\n\n## Tasks\n- [ ] Research providers\n- [ ] Design flow\n- [ ] Implement" \
  --epic ODT-123 \
  --component "Authentication" \
  --priority "Medium" \
  --labels "feature,auth"
```

The upload command will:
- Convert markdown formatting to Jira markup
- Validate all inputs (epic, component, priority) before creating the issue
- Handle epic links appropriately (disabled when creating epics)
- Use project configuration from your jiragen config file

## Environment Variables

Configure JiraGen behavior through environment variables:

```bash
JIRAGEN_CONFIG_PATH      # Custom config file location
JIRAGEN_MODEL           # Default LLM model
JIRAGEN_API_BASE        # Ollama API endpoint
JIRAGEN_TEMPLATE_DIR    # Template directory path
```

## Exit Codes

- `0`: Success
- `1`: General error or operation cancelled by user

## Data Storage

JiraGen stores its data following the XDG Base Directory specification:

### Unix-like Systems (Linux, macOS)

```
~/.config/jiragen/           # Configuration directory
└── config.ini              # Main configuration file
```
