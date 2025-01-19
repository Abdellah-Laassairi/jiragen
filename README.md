# JiraGen: Automated JIRA Issue Generation

<p align="center">
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

**Jiragen** is a CLI designed to automate the creation of JIRA Issues through the use of Local Large Language Models (LLMs). It leverages the power of Ollama and LiteLLM to provide context-aware issue generation, enabling efficient and effective interaction with JIRA. Full documentation is available [here](https://github.com/Abdellah-Laassairi/jiragen).

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
- 🔍 **Context-Aware Issues**: Incorporates relevant context using Vector store integration for scalable context handling.
- ✨ **Customizable Templates**: Adapt issue formats to your needs.
- 🔧 **Metadata Extraction**: Automates technical details from codebases.
- ⚙️ **Configurable Parameters**: Fine-tune the generation process.

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
jiragen rm path/to/files      # Remove files from vector store
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
    max_tokens=2000,
    temperature=0.7,
    top_p=0.95,
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
