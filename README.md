# JiraGen: Automated JIRA Ticket Generation with Local LLMs

<p align="center">
  <img src="https://img.shields.io/github/stars/Abdellah-Laassairi/jiragen?style=social" alt="GitHub Repo stars"/>
  <img src="https://img.shields.io/github/forks/Abdellah-Laassairi/jiragen?style=social" alt="GitHub Repo forks"/>
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

**JiraGen** is a CLI designed to automate the creation of JIRA tickets through the use of Local Large Language Models (LLMs). It leverages the power of Ollama and LiteLLM to provide context-aware ticket generation, enabling efficient and effective interaction with JIRA.

---

## 📖 Table of Contents

- [Key Features](#key-features)
- [Quick Start](#quick-start)
- [Configuration Options](#configuration-options)
- [Template Customization](#template-customization)
- [Contributing](#contributing)
- [License](#license)

## 🌟 Key Features

- 🧠 **Local LLM Integration**: Leverages Ollama and LiteLLM.
- 🔍 **Context-Aware Tickets**: Incorporates relevant context using Vector store integration for scalable context handling.
- ✨ **Customizable Templates**: Adapt ticket formats to your needs.
- 🔧 **Metadata Extraction**: Automates technical details from codebases.
- ⚙️ **Configurable Parameters**: Fine-tune the generation process.

## ⚡ Quick Start

### Installation

Install JiraGen and its dependencies:

```bash
pip install jiragen
```

Install & runOllama to use your local LLM:

```bash
curl https://ollama.ai/install.sh | sh
ollama pull phi4  # Replace with your preferred model
```

### Command Line Interface

JiraGen provides a powerful CLI for efficient ticket generation and management:

```bash
# Init
jiragen init

# Basic ticket generation
jiragen generate "Implement user authentication system"

# Generate with specific template
jiragen generate -t templates/custom.txt "Add API rate limiting"

# Generate with custom LLM configuration
jiragen generate --model codellama --temperature 0.8 "Refactor database schema"

# Status and management commands
jiragen status                    # Display vector store status
jiragen status --compact          # Show compact status view
jiragen status --depth 2          # Limit directory tree depth

# Vector store operations
jiragen add path/to/files         # Add files to vector store
jiragen remove path/to/files      # Remove files from vector store
```

### API Usage

```python
from jiragen import TicketGenerator, LLMConfig, GeneratorConfig
from pathlib import Path

# Configure the generator
config = GeneratorConfig(
    template_path=Path("templates/jira_template.txt"),
    llm_config=LLMConfig(model="llama2", api_base="http://localhost:11434"),
)

# Initialize the generator
generator = TicketGenerator(vector_store_client, config)

# Generate a ticket
ticket = generator.generate("Implement user authentication using JWT")
```

## ⚙️ Configuration Options

JiraGen supports a variety of configuration parameters to tailor ticket generation:

```python
LLMConfig(
    model="llama2",  # Ollama model to use
    api_base="http://localhost:11434",  # Ollama endpoint
    max_tokens=2000,  # Maximum response length
    temperature=0.7,  # Generation creativity
    top_p=0.95,  # Nucleus sampling parameter
)
```

## 📝 Template Customization

Create templates to match your organization's needs:

```text
Title: {title}
Type: {type}
Priority: {priority}

Description:
{description}

Acceptance Criteria:
{acceptance_criteria}

Technical Implementation:
{implementation_details}
```

## 🤝 Contributing

We ❤️ contributions! To contribute:

1. Fork the repository.
2. Create a feature branch.
3. Submit a pull request with a detailed description of your changes.

For more details, refer to our [CONTRIBUTING.md](CONTRIBUTING.md).

## 📜 License

JiraGen is released under the [MIT License](LICENSE).
