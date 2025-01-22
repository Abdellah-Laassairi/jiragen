# CLI Overview

JiraGen provides a powerful command-line interface for managing JIRA issue generation and codebase integration. This section covers all available commands and their usage.

## Command Structure

```bash
jiragen [command] [options] [arguments]
```

## Available Commands

- `init`: Initialize JiraGen in your project
- `generate`: Generate JIRA issues with AI assistance
- `add`: Add files to the vector store
- `rm`: Remove files from the vector store
- `fetch`: Fetch JIRA data
- `status`: Check vector store status
- `upload`: Upload issues to JIRA
- `restart`: Restart the vector store service

See the following sections for detailed documentation on each command.

## Global Options

- `--verbose`: Enable detailed logging
- `--config PATH`: Use custom config file
- `--help`: Show command help

## Command Categories

### [Basic Commands](basic.md)
Core commands for managing JiraGen's configuration and basic operations:
- `init`: Initialize JiraGen configuration
- `status`: Display vector store status
- `restart`: Restart vector store service
- `clean`: Clean vector store database

### [Codebase Management](codebase.md)
Commands for managing your codebase in the vector store:
- `add`: Add files to vector store (with gitignore support)
- `rm`: Remove files from vector store
- `fetch`: Fetch JIRA data for context

### [Issue Generation](generate.md)
Commands for generating and managing JIRA issues:
- `generate`: Generate issues with AI assistance
- `upload`: Upload issues to JIRA

### [JIRA Integration](jira.md)
Commands for interacting with JIRA:
- `fetch`: Fetch JIRA data
- `upload`: Upload issues
- `sync`: Synchronize local and remote data

## Common Workflows

### 1. Initial Setup
```bash
# Initialize JiraGen
jiragen init

# Add your codebase
jiragen add .

# Fetch JIRA data for context
jiragen fetch --types all
```

### 2. Issue Generation
```bash
# Generate a new issue
jiragen generate "Add dark mode support"

# Generate and upload directly
jiragen generate "Fix memory leak" --upload --yes
```

### 3. Codebase Updates
```bash
# Add new files
jiragen add src/new_feature/

# Remove old files
jiragen rm src/deprecated/

# Check status
jiragen status --compact
```

## Exit Codes

JiraGen commands return these exit codes:

- `0`: Success
- `1`: General error or operation cancelled by user
- `2`: Configuration error
- `3`: Network error
- `4`: Permission error
