# JIRA Integration

This section covers commands for interacting with JIRA, including fetching data and uploading issues.

## fetch

Fetch JIRA data to provide context for issue generation.

```bash
jiragen fetch [OPTIONS]
```

### Options
- `--types TYPE [TYPE...]`: Types of data to fetch (default: `tickets,epics`)
  - Available types: `epics`, `tickets`, `components`
  - Use `all` to fetch everything
- `--project KEY`: Specific project to fetch from
- `--since DAYS`: Only fetch issues updated in last N days
- `--limit N`: Maximum number of items to fetch
- `--force`: Force refresh cached data

### Examples

```bash
# Fetch all data types
jiragen fetch --types all

# Fetch specific types
jiragen fetch --types epics tickets

# Fetch recent issues from a project
jiragen fetch --project PROJ --since 30

# Force refresh with limit
jiragen fetch --types all --force --limit 1000
```

### Output Format

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
```

## upload

Upload issues directly to JIRA.

```bash
jiragen upload [OPTIONS]
```

### Required Options
- `--title TEXT`: Issue title/summary

### Optional Options
- `--description TEXT`: Issue description (supports markdown)
- `--type TEXT`: Issue type (Story, Bug, Task, Epic, etc.)
- `--epic KEY`: Epic key to link to (e.g., `PROJ-123`)
- `--component TEXT`: Component name
- `--priority TEXT`: Priority level
- `--labels TEXT`: Comma-separated labels
- `--assignee TEXT`: Assignee username
- `--reporter TEXT`: Reporter username
- `--project KEY`: Project key (overrides default)

### Examples

```bash
# Upload basic issue
jiragen upload --title "Add user authentication"

# Upload with full metadata
jiragen upload \
  --title "Implement OAuth2" \
  --type Feature \
  --description "Add OAuth2 authentication support" \
  --epic PROJ-100 \
  --component Backend \
  --priority High \
  --labels "security,auth" \
  --assignee "john.doe"

# Upload from file
jiragen upload --from-file issue.md
```

## sync

Synchronize local and remote JIRA data.

```bash
jiragen sync [OPTIONS]
```

### Options
- `--direction`: Sync direction (`pull`, `push`, `both`)
- `--types`: Data types to sync
- `--dry-run`: Show what would be synced
- `--force`: Force sync even if no changes detected

### Examples

```bash
# Full sync
jiragen sync

# Pull only
jiragen sync --direction pull

# Dry run
jiragen sync --dry-run

# Force sync specific types
jiragen sync --types epics,components --force
```

## Best Practices

1. **Data Freshness**:
   - Run `fetch` regularly to keep context updated
   - Use `--since` to fetch recent changes
   - Consider setting up automated sync

2. **Upload Strategy**:
   - Review generated content before upload
   - Use consistent metadata
   - Link related issues appropriately

3. **Project Organization**:
   - Use epics for grouping related issues
   - Apply consistent labeling
   - Assign components correctly

4. **Performance**:
   - Use `--limit` for large projects
   - Cache data when possible
   - Schedule bulk operations off-peak
```
