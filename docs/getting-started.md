# Getting Started

This guide will help you get up and running with JiraGen.

## Installation

Install JiraGen using pip:

```bash
pip install jiragen
```

## Configuration

### 1. Initialize JiraGen

First, initialize JiraGen in your project directory:

```bash
jiragen init
```

This will create a `.jiragen` directory with the following structure:
```
.jiragen/
├── config.ini
├── templates/
│   └── default.md
└── vector_store/
```

### 2. Configure JIRA Settings

Edit `.jiragen/config.ini` to add your JIRA credentials:

```ini
[jira]
url = https://your-domain.atlassian.net
username = your-email@example.com
api_token = your-api-token

[llm]
model = openai/gpt-4o
temperature = 0.7
max_tokens = 2000

[vector_store]
path = .jiragen/vector_store
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
1. Scan your codebase
2. Create embeddings for relevant files
3. Store them in the vector store

## Basic Usage

### Generate a Ticket

```bash
jiragen generate "Add dark mode support"
```

This will:
1. Search your codebase for relevant context
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

Create custom templates in `.jiragen/templates/`:

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
