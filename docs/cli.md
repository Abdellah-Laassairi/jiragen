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

Initialize JiraGen configuration

```bash
jiragen init
```

This command will prompt you to enter your JIRA configuration, including URL, username, API token, default project, and default assignee.

**Options:**
- `-c, --config PATH`: Specify custom config file location

### generate

Generate JIRA tickets

```bash
jiragen generate [OPTIONS] DESCRIPTION

Options:
  -t, --template PATH    : Custom template path
  -m, --model NAME      : LLM model name
  --temperature FLOAT   : Model temperature (0.0-1.0)
  --max-tokens INT      : Maximum token limit
  -o, --output PATH     : Output file path
```

### fetch

Fetch JIRA data and store it in a separate vector store

```bash
jiragen fetch [OPTIONS]

Options:
 --all                 : Fetch all JIRA data
 --issue               : Fetch JIRA issues
 --comment             : Fetch JIRA comments
 --project             : Fetch JIRA projects
 --component           : Fetch JIRA components
 --epic                : Fetch JIRA epics
```

### status

Display vector store status

```bash
jiragen status [OPTIONS]

Options:
  -c, --compact         : Show compact view
  -d, --depth INT      : Set directory tree depth
```

### add

Add files to vector store

```bash
jiragen add [OPTIONS] PATH [PATH...]

Options:
  -r, --recursive      : Add directories recursively
  --ignore PATTERN     : Ignore files matching pattern
```

### remove

Remove files from vector store

```bash
jiragen remove [OPTIONS] PATH [PATH...]

Options:
  -r, --recursive      : Remove directories recursively
  --force             : Skip confirmation
```

## Environment Variables

Configure JiraGen behavior through environment variables:

```bash
JIRAGEN_CONFIG_PATH      # Custom config file location
JIRAGEN_MODEL           # Default LLM model
JIRAGEN_API_BASE        # Ollama API endpoint
JIRAGEN_TEMPLATE_DIR    # Template directory path
```

## Exit Codes

JiraGen CLI follows standard Unix exit codes:

- `0`: Success
- `1`: General error
- `2`: Invalid command usage
- `3`: Configuration error
- `4`: Vector store error
- `5`: LLM error

This structured CLI documentation provides precise control over JiraGen's functionality while maintaining consistency with Unix command-line conventions and best practices.

For programmatic interaction with the CLI, consider the exit codes when implementing automation or scripting solutions.
