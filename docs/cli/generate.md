# Issue Generation

This section covers commands for generating and managing JIRA issues using AI assistance.

## generate

Generate JIRA issues with AI-powered context from your codebase.

```bash
jiragen generate MESSAGE [OPTIONS]
```

### Arguments
- `MESSAGE`: Description of the issue to generate (required)

### Options
- `-t, --template PATH`: Path to template file (default: `default.md`)
- `-m, --model NAME`: LLM model to use (default: `gpt-4`)
- `--temperature FLOAT`: Model temperature (0.0-1.0) (default: 0.7)
- `--max-tokens INT`: Maximum tokens to generate (default: 2000)
- `-e, --editor`: Open editor for manual editing
- `-u, --upload`: Upload issue to JIRA after generation
- `-y, --yes`: Skip all confirmations and use defaults
- `--epic KEY`: Link to epic (e.g., `PROJ-123`)
- `--type TYPE`: Issue type (default: Story)
- `--priority PRIORITY`: Issue priority
- `--labels LABELS`: Comma-separated labels
- `--components COMPONENTS`: Comma-separated components

### Interactive Workflow

1. **Content Generation**:
   ```bash
   $ jiragen generate "Add dark mode support"

   🔍 Searching codebase for context...
   ✨ Generating issue content...

   # Add dark mode support

   ## Description
   Implement dark mode theme support across the application...

   Would you like to edit the content? [Y/n]:
   ```

2. **Metadata Extraction**:
   ```bash
   Generated Metadata:
   - Type: Feature
   - Priority: Medium
   - Labels: frontend, UI, theme
   - Components: UI
   - Story Points: 5

   Would you like to modify the metadata? [y/N]:
   ```

3. **JIRA Upload** (with `-u`):
   ```bash
   Do you want to upload this issue to JIRA? [Y/n]:
   ✓ Created JIRA issue: PROJ-456
   ```

### Examples

```bash
# Basic generation
jiragen generate "Add user authentication"

# Generate with custom template
jiragen generate "Fix memory leak" --template bug.md

# Generate and upload with specific metadata
jiragen generate "Add OAuth support" \
  --upload \
  --type Feature \
  --priority High \
  --labels "security,auth" \
  --components "Backend"

# Generate and upload automatically
jiragen generate "Update dependencies" --upload --yes

# Generate with custom model settings
jiragen generate "Optimize database queries" \
  --model gpt-4 \
  --temperature 0.8 \
  --max-tokens 2500
```

### Best Practices

1. **Message Format**:
   - Be clear and concise
   - Include key requirements
   - Specify the scope

2. **Template Selection**:
   - Use `bug.md` for bugs
   - Use `feature.md` for features
   - Create custom templates for specific needs

3. **Metadata Management**:
   - Review extracted metadata
   - Adjust priorities appropriately
   - Use consistent labeling

4. **Interactive Mode**:
   - Review generated content
   - Verify technical details
   - Check acceptance criteria
