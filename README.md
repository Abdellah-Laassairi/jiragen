# JiraGen: Automated JIRA Issue Generation

<p align="left">
  <a href="LICENSE">
    <img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License"/>
  </a>
  <a href="https://python.org">
    <img src="https://img.shields.io/badge/python-3.10+-blue.svg" alt="Python 3.10+"/>
  </a>
  <img src="https://img.shields.io/badge/PRs-Welcome-brightgreen.svg" alt="PRs Welcome"/>
  <img src="https://img.shields.io/badge/platform-local-lightgrey" alt="Platform: Local"/>
</p>

## 🚀 Overview

**Jiragen** is a CLI designed to automate the creation of JIRA Issues through the use of Large Language Models (LLMs). It is fully integrated with JIRA API and your Local codebase accelerating jira issue creation and enabling developers to focus on other aspects of their projects. Full documentation is available [here](https://github.com/Abdellah-Laassairi/jiragen).

---

## 📖 Table of Contents

- [Key Features](#key-features)
- [Quick Start](#quick-start)
- [Usage Examples](#usage-examples)
- [Configuration Options](#configuration-options)
- [Template Customization](#template-customization)
- [Contributing](#contributing)
- [License](#license)

## 🌟 Key Features

- 🧠 **Local LLM Integration**: Leverages Ollama (via LiteLLM) for local text generation
- 🔍 **Context-Aware Issues**: Smart codebase analysis with vector store integration
- 🎯 **Gitignore Support**: Respects .gitignore patterns when indexing codebase
- ✨ **Customizable Templates**: Flexible issue templates for different needs
- 🔧 **Smart Metadata Extraction**: Automatic extraction of issue type, priority, and labels
- ⚙️ **Interactive Workflow**: Review and modify content before uploading

## ⚡ Quick Start

### Installation

Install JiraGen and its dependencies:

```bash
pip install jiragen
```

Install & run Ollama to use your local LLM:

```bash
curl https://ollama.ai/install.sh | sh
ollama pull phi4  # Replace with your preferred model
```

or export your OpenAI API key:

```bash
export OPENAI_API_KEY="YOUR_API_KEY"
```

### Basic Setup

```bash
# Initialize configuration
jiragen init

# Index your codebase (respects .gitignore)
jiragen add .

# Generate your first issue
jiragen generate "Implement user authentication"
```

## 🎯 Usage Examples

### Codebase Indexing

```bash
# Add all files (respects .gitignore)
jiragen add .

# Add specific files or directories
jiragen add src/main.py

# Remove files
jiragen rm src/deprecated/
```

### Issue Generation

```bash
# Basic generation
jiragen generate "Add dark mode support"

# With custom template and model
jiragen generate "API rate limiting" \
  --template templates/feature.md \
  --model ollama/codellama

# Generate and upload to JIRA
jiragen generate "Fix memory leak" --upload --yes

# Interactive editing
jiragen generate "OAuth integration" --editor
```

### Status and Management

```bash
# View indexed files
jiragen status
jiragen status --compact
jiragen status --depth 2

# Fetch JIRA data
jiragen fetch --types epics tickets

# Restart vector store
jiragen restart
```

## ⚙️ Configuration Options

JiraGen can be configured through:
- Command-line arguments
- Configuration file (`~/.jiragen/config.ini`)
- Environment variables

```python
# Python API configuration
LLMConfig(
    model="llama2",  # Ollama model to use
    api_base="http://localhost:11434",  # Ollama endpoint
    max_tokens=2000,
    temperature=0.7,
    top_p=0.95,
)
```

## 📝 Template Customization

Create templates to match your organization's needs:

```markdown
# {title}

## Description
{description}

## Acceptance Criteria
{acceptance_criteria}

## Technical Implementation
{implementation_details}

## Testing Strategy
- Unit Tests
- Integration Tests
- E2E Tests
```

## 🤝 Contributing

We ❤️ contributions! To contribute:

1. Fork the repository
2. Create a feature branch
3. Submit a pull request with a detailed description

For more details, refer to our [CONTRIBUTING.md](CONTRIBUTING.md).

## 📜 License

JiraGen is released under the [MIT License](LICENSE).
