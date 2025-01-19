# JiraGen: AI-Powered JIRA Issue Generation

JiraGen is a powerful command-line tool that leverages AI to generate high-quality JIRA isses with context from your codebase. It streamlines the isse creation process by automatically extracting relevant metadata and providing an interactive workflow for isse refinement.

## Features

- **AI-Powered Generation**: Uses advanced language models (OpenAI GPT-4 by default) to generate detailed isse descriptions
- **Codebase Context**: Incorporates relevant code snippets and documentation from your codebase
- **Interactive Workflow**: Edit content and metadata before uploading
- **Smart Metadata**: Automatically extracts issue type, priority, labels, and components
- **JIRA Integration**: Seamlessly upload isses to your JIRA instance
- **Fast & Efficient**: Vector store-based search for quick context retrieval
- **Template Support**: Customizable templates for consistent isse format

## Quick Start

1. Install JiraGen:

```bash
pip install jiragen
```

2. Initialize in your project:

```bash
jiragen init
```

3. Add your codebase to the vector store:

```bash
jiragen add .
```

4. Generate a isse:

```bash
jiragen generate "Add dark mode support" --upload
```

## Example Usage

### Basic isse Generation

```bash
# Generate a isse with default settings
jiragen generate "Implement user authentication"

# Generate and upload with automatic metadata
jiragen generate "Fix memory leak in worker process" --upload --yes

# Use custom model and template
jiragen generate "Add OAuth support" --model openai/gpt-4 --template feature.md
```

### Interactive Features

- Edit generated content in your preferred editor
- Review and modify extracted metadata
- Confirm before uploading to JIRA

## Configuration

JiraGen can be configured through:

- Command-line arguments
- Configuration file (`~/.jiragen/config.ini`)
- Environment variables

See the [Getting Started](getting-started.md) guide for detailed configuration instructions.

## Documentation

- [Getting Started Guide](getting-started.md)
- [CLI Reference](cli.md)
- [API Documentation](api/core.md)

## Contributing

We welcome contributions! Check out our [Contributing Guide](https://github.com/Abdellah-Laassairi/jiragen/blob/main/CONTRIBUTING.md) to get started.

## License

JiraGen is licensed under the MIT License. See the [LICENSE](https://github.com/Abdellah-Laassairi/jiragen/blob/main/LICENSE) file for details.
