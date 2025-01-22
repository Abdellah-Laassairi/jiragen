# Codebase Management

This section covers commands for managing your codebase in the vector store.

## add

Add files to the vector store database. Supports .gitignore patterns and recursive directory scanning.

```bash
jiragen add PATH [PATH...]

Arguments:
  PATH               : One or more files or directories to add to the database
                      Use "." to add all files in current directory recursively
                      Use "*" to add all files in current directory only
                      Use specific paths for individual files or directories
```

### Features

- **Gitignore Support**: Automatically respects .gitignore patterns
- **Progress Tracking**: Shows progress bar and statistics
- **Tree View**: Visual display of added files
- **Directory Scanning**: Recursive scanning of directories
- **Pattern Matching**: Supports glob patterns

### Examples

```bash
# Add all files recursively (respects .gitignore)
jiragen add .

# Add specific files
jiragen add src/main.py tests/test_api.py

# Add all files in a specific directory
jiragen add src/

# Add all Python files in current directory
jiragen add *.py
```

Example output:
```
📁 Added Files
├── src/main.py
├── src/utils/helper.py
└── tests/test_api.py

Successfully added 3 files (52.7 files/second)
```

## rm (remove)

Remove files from the vector store database.

```bash
jiragen rm PATH [PATH...]

Arguments:
  PATH               : One or more files or directories to remove
                      Supports the same patterns as the add command
```

### Examples

```bash
# Remove specific files
jiragen rm src/deprecated.py

# Remove all files in a directory
jiragen rm old_code/

# Remove files matching a pattern
jiragen rm *.tmp
```

Example output:
```
🗑️  Removed Files
├── src/deprecated.py
└── old_code/helper.py

Successfully removed 2 files
```

## fetch

Fetch JIRA data and store it in a separate vector store.

```bash
jiragen fetch [OPTIONS]

Options:
  --types TYPE [TYPE...]  : Types of data to fetch (default: tickets, epics)
                           Available types: epics, tickets, components
                           Use 'all' to fetch everything
```

### Examples

```bash
# Fetch all JIRA data types
jiragen fetch --types all

# Fetch specific types
jiragen fetch --types epics tickets
```

Example output:
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

✨ Fetch completed successfully!
⏱️  Time taken: 5.23 seconds
📁 Data stored in: ~/.local/share/jiragen/jira_data
```

The fetched data is stored in the system's data directory following the XDG Base Directory specification:

**Unix-like Systems (Linux, macOS)**:
- `~/.local/share/jiragen/jira_data/epics/`
- `~/.local/share/jiragen/jira_data/tickets/`
- `~/.local/share/jiragen/jira_data/components/`

**Windows**:
- `%LOCALAPPDATA%\jiragen\jira_data\epics\`
- `%LOCALAPPDATA%\jiragen\jira_data\tickets\`
- `%LOCALAPPDATA%\jiragen\jira_data\components\`

Each item is stored in both JSON and Markdown formats for easy viewing and processing.
