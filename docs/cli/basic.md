# Basic Commands

This section covers the essential commands you'll use most frequently with JiraGen.

## Global Options

All JiraGen commands support these global options:

```bash
--verbose            : Enable detailed logging
--config PATH       : Specify custom config file location
--help              : Display command help
```

## init

Initialize JiraGen in your project:

```bash
jiragen init [OPTIONS]
```

Options:
- `--force`: Overwrite existing configuration
- `--skip-validation`: Skip JIRA connection validation

The init command:
1. Creates necessary directories
2. Generates default configuration
3. Validates JIRA connection
4. Sets up vector store

## status

Check the status of your vector store and JIRA synchronization:

```bash
jiragen status [OPTIONS]
```

Options:
- `--compact`: Show compact view
- `--depth INT`: Maximum directory depth to display

Example output:
```
📊 Vector Store Status
Files indexed: 156
Last updated: 2024-01-22 12:30:45
Size: 25.4 MB

🔄 JIRA Sync Status
Last sync: 2024-01-22 12:00:00
Issues cached: 234
Components: 12
```

## restart

Restart the vector store service:

```bash
jiragen restart [OPTIONS]
```

Options:
- `--hard`: Clear cache before restart
- `--timeout SEC`: Maximum wait time (default: 30)

Use this command if you experience:
- Connection issues
- Performance degradation
- Unexpected behavior

## clean

Remove all files from the vector store database.

```bash
jiragen clean
```

Example output:
```
🗑️  Cleaning vector store...
✨ Vector store cleaned successfully
```
