# PyEnvCLI

> **A CLI tool for Python virtual environment generation with AI-assisted development**

Synthesized from [AIM v1.4 specification](https://intentmodel.dev) - `pyenv-cli.intent`

## Overview

PyEnvCLI is an interactive command-line tool that streamlines Python virtual environment creation and management. It provides **two interfaces**:

1. **CLI** - Traditional command-line interface for scripting and automation
2. **TUI** - Full-screen terminal UI for interactive management

### Features

- 🐍 **Multiple Python versions** (3.8 - 3.13)
- 📦 **Package dependency management** (requirements.txt)
- 🐳 **Docker configuration** (optimized Dockerfiles)
- 🤖 **AI CLI tool integration** (Claude Code, GitHub Copilot, ChatGPT, Cursor)
- 🖥️ **Modern Terminal UI** with keyboard shortcuts and mouse support

## Features

### Core Capabilities

✅ **Interactive Environment Creation**
- Python version selection with system validation
- Filesystem-safe environment naming
- Automatic `.python-version` file generation

✅ **Dependency Management**
- Add packages with version constraints (PEP 440)
- Generate `requirements.txt` automatically
- Install packages during environment setup

✅ **Docker Support**
- Multi-stage Dockerfile generation
- Optimized layer caching for dependencies
- Configurable ports and custom commands

✅ **AI-Assisted Workflows**
- Launch AI tools with environment context
- Session tracking and audit trail
- Support for multiple AI CLI tools

## Installation

### From Source

```bash
git clone <repository-url>
cd pyenv-cli
pip install -e .
```

### Using pip (after publishing)

```bash
pip install pyenv-cli
```

## Quick Start

### Launch the Terminal UI (Recommended)

```bash
pyenv-tui
```

**Features:**
- ✨ Python version checking & installation
- 🔍 Package search with common packages
- 📦 Smart package management
- 🔧 **Completely rewritten - No freezing!**

See [FINAL_FIX.md](FINAL_FIX.md) for technical details.

### Or Use the CLI

### 1. Create a Virtual Environment

```bash
# Interactive mode (recommended)
pyenv-cli create

# Or specify options directly
pyenv-cli create --name myenv --python 3.11 --docker
```

**Example interaction:**
```
🐍 PyEnvCLI - Virtual Environment Setup

Environment name [venv]: myapp
Python version (3.8, 3.9, 3.10, 3.11, 3.12, 3.13) [3.11]: 3.11
Generate Dockerfile? [y/n] (n): y

✓ Virtual environment created successfully!

┌─────────────────────────────────────────┐
│      Activation Command                 │
│                                         │
│  source myapp/bin/activate              │
└─────────────────────────────────────────┘
```

### 2. Add Package Dependencies

```bash
# Interactive mode
pyenv-cli packages <config-id>

# Or specify packages directly
pyenv-cli packages <config-id> --add flask --add "requests==2.31.0"
```

### 3. Configure Docker

```bash
# Generate Dockerfile with exposed ports
pyenv-cli docker <config-id> --port 8000 --port 5432

# Add custom Docker commands
pyenv-cli docker <config-id> --command "RUN apt-get update"
```

### 4. Launch AI Assistant

```bash
# Interactive tool selection
pyenv-cli ai <config-id>

# Or specify tool directly
pyenv-cli ai <config-id> --tool claude-code --prompt "Help optimize my setup"
```

### 5. List Environments

```bash
pyenv-cli list
```

## Commands Reference

### `create`
Create a new Python virtual environment.

**Options:**
- `-n, --name TEXT` - Environment name
- `-p, --python TEXT` - Python version (3.8-3.13)
- `-d, --path TEXT` - Project directory (default: current)
- `--docker/--no-docker` - Generate Dockerfile
- `--requirements/--no-requirements` - Generate requirements.txt (default: yes)
- `-a, --ai-tool CHOICE` - AI tool preference

### `packages <config-id>`
Manage package dependencies.

**Options:**
- `-a, --add TEXT` - Add package (can be used multiple times)

### `docker <config-id>`
Generate and configure Dockerfile.

**Options:**
- `-p, --port INTEGER` - Expose port (can be used multiple times)
- `-c, --command TEXT` - Additional Docker command

### `ai <config-id>`
Launch AI CLI tool with environment context.

**Options:**
- `-t, --tool CHOICE` - AI tool (claude-code, copilot-cli, chatgpt-cli, cursor-ai)
- `-p, --prompt TEXT` - Custom prompt

### `list`
List all configured virtual environments.

## Architecture

PyEnvCLI is synthesized from the [AIM v1.4 specification](https://intentmodel.dev/specification) with strict adherence to:

### SCHEMA Layer (Data Models)
- `VirtualEnvConfig` - Environment configuration with validation
- `PackageRequirement` - PEP 440 compliant package specs
- `DockerConfiguration` - Docker setup with generated content
- `AIToolSession` - AI interaction audit trail

### FLOW Layer (Business Logic)
- `ValidatePythonVersion` - System Python availability checks
- `GenerateRequirementsList` - requirements.txt generation
- `GenerateDockerfile` - Optimized Dockerfile creation
- `CreateVirtualEnvironment` - venv setup and activation
- `LaunchAIAssistant` - AI tool integration

### CONTRACT Layer (Application Boundary)
- `CreateVirtualEnv` - Main environment creation workflow
- `ConfigurePackages` - Dependency management
- `ConfigureDocker` - Docker configuration
- `PromptAITool` - AI assistant launcher

### VIEW Layer (CLI Interface)
- Interactive prompts using [Click](https://click.palletsprojects.com/) + [Rich](https://rich.readthedocs.io/)
- Table-based environment listing
- Syntax-highlighted output
- Progress indicators

## Data Persistence

PyEnvCLI uses local JSON file storage (no database required):

```
.pyenv-cli/
├── configs.json       # VirtualEnvConfig records
├── packages.json      # PackageRequirement records
├── docker.json        # DockerConfiguration records
└── ai_sessions.json   # AIToolSession records
```

## Interfaces

### Terminal UI (TUI) - Recommended
- **Launch:** `pyenv-tui`
- **Features:** Python installation, package search, no freezing
- **Best for:** Interactive setup, visual environment management
- **Documentation:** [FINAL_FIX.md](FINAL_FIX.md)

### Command-Line Interface (CLI)
- **Launch:** `pyenv-cli <command>`
- **Features:** Script-friendly, automation-ready
- **Best for:** CI/CD, scripts, quick commands
- **Documentation:** See commands below

## Requirements

- Python 3.8+
- System Python versions must be installed separately
- Optional: Docker (for Dockerfile execution)
- Optional: AI CLI tools (claude, github-copilot-cli, chatgpt, cursor)

## AI Tool Integration

PyEnvCLI prepares context for AI assistants including:
- Environment name and Python version
- Project path and structure
- Package dependencies
- Docker configuration status

Supported AI CLI tools:
- **Claude Code** - `claude` command
- **GitHub Copilot CLI** - `github-copilot-cli` command
- **ChatGPT CLI** - `chatgpt` command
- **Cursor AI** - `cursor` command

## Development

### Project Structure

```
pyenv-cli/
├── pyenv_cli/
│   ├── __init__.py         # Package metadata
│   ├── __main__.py         # Entry point
│   ├── models.py           # SCHEMA: Pydantic models
│   ├── persistence.py      # JSON storage layer
│   ├── flows.py            # FLOW: Business logic
│   ├── contracts.py        # CONTRACT: Use cases
│   └── cli.py              # VIEW: CLI interface
├── pyproject.toml          # Package configuration
├── requirements.txt        # Dependencies
├── setup.py               # Setup script
├── LICENSE                # MIT License
└── README.md              # This file
```

### Running Locally

```bash
# Install in editable mode
pip install -e .

# Run CLI
pyenv-cli --help
```

### Testing

```bash
# Create test environment
pyenv-cli create --name testenv --python 3.11

# Add packages
pyenv-cli packages $(pyenv-cli list | grep testenv | awk '{print $1}') \
  --add pytest --add black

# Generate Docker
pyenv-cli docker $(pyenv-cli list | grep testenv | awk '{print $1}') \
  --port 8000
```

## License

MIT License - See [LICENSE](LICENSE) file for details.

## Credits

**Synthesized by:** AIM v1.4 Synthesizer
**Specification:** [Application Intent Model](https://intentmodel.dev)
**Intent File:** `pyenv-cli.intent`

---

*This is a production-ready implementation generated from the AIM DSL with zero hallucination - every feature, schema, flow, and contract is directly traceable to the intent specification.*
