# PyEnvCLI Terminal User Interface (TUI) Guide

## Overview

The PyEnvCLI TUI provides a full-screen, interactive terminal interface for managing Python virtual environments. Built with [Textual](https://textual.textualize.io/), it offers a modern, keyboard-driven experience with mouse support.

## Installation & Launch

### 1. Install PyEnvCLI with TUI support

```bash
cd pyenv-cli
pip install -e .
```

This installs:
- `pyenv-cli` - The traditional CLI interface
- `pyenv-tui` - The new Terminal UI

### 2. Start the TUI

```bash
pyenv-tui
```

Or run directly with Python:

```bash
python -m pyenv_cli.tui
```

## Features

### 🏠 Main Dashboard (Welcome Screen)

The main screen displays all configured virtual environments in a table format.

**Navigation:**
- `↑`/`↓` or mouse - Select environment
- `Enter` or click - Open environment details
- `n` - Create new environment
- `r` - Refresh list
- `q` - Quit application

**Table Columns:**
- **ID** - Short identifier (first 8 chars)
- **Name** - Environment name
- **Python** - Python version
- **Docker** - Dockerfile generation status (✓/✗)
- **Created** - Creation timestamp

### ➕ Create Environment Screen

Interactive form for creating new Python virtual environments.

**Fields:**
- **Environment Name** - Filesystem-safe name (alphanumeric, hyphens, underscores)
- **Python Version** - Dropdown with 3.8-3.13
- **Project Path** - Directory path (default: current directory)
- **Generate Dockerfile** - Checkbox
- **Generate requirements.txt** - Checkbox (default: checked)
- **AI Tool Preference** - Optional AI assistant selection

**Actions:**
- `Create` button - Execute environment creation
- `Cancel` button or `Esc` - Return to dashboard

**Validation:**
- Real-time Python version availability check
- Environment name pattern validation
- Project path existence verification

### 📁 Environment Detail Screen

Shows detailed information and management options for a selected environment.

**Information Displayed:**
- Configuration ID
- Python version
- Project path
- Docker status
- Requirements status
- AI tool preference
- Creation timestamp
- List of installed packages

**Actions:**
- `📦 Manage Packages` (`p` key) - Add/remove dependencies
- `🐳 Configure Docker` (`d` key) - Generate Dockerfile
- `🤖 Launch AI Tool` (`a` key) - Start AI assistant
- `← Back` or `Esc` - Return to dashboard

### 📦 Manage Packages Screen

Add Python package dependencies to the environment.

**Workflow:**
1. Enter package name (e.g., `flask`, `requests`)
2. Enter version constraint (optional, e.g., `==2.31.0`, `>=1.0.0`)
3. Click "Add Package" - Package added to pending list
4. Repeat for additional packages
5. Click "Save All" - Generates requirements.txt

**Features:**
- PEP 440 version specifier support
- Multiple packages in single session
- Preview pending packages before saving
- Automatic requirements.txt generation

### 🐳 Configure Docker Screen

Generate optimized Dockerfile for the environment.

**Configuration Options:**
- **Exposed Ports** - Comma-separated port numbers (e.g., `8000,5432`)
- **Additional Commands** - Custom Dockerfile instructions (2 input fields)

**Generated Dockerfile Features:**
- Multi-stage build support
- Dependency layer caching
- Official Python slim images
- Port exposure
- Custom build commands

**Actions:**
- `Generate Dockerfile` - Create Dockerfile in project directory
- `Cancel` or `Esc` - Return to environment details

### 🤖 Launch AI Assistant Screen

Prepare and launch AI CLI tools with environment context.

**Options:**
- **AI Tool Selection** - Choose from:
  - Claude Code
  - GitHub Copilot CLI
  - ChatGPT CLI
  - Cursor AI
- **Custom Prompt** - Describe what you need help with

**Context Provided to AI:**
- Environment name and Python version
- Project path
- Installed packages
- Docker configuration status
- User's custom prompt

**Features:**
- Tool availability checking
- Session tracking
- Context preparation
- Launch instructions

## Keyboard Shortcuts

### Global
- `Ctrl+C` - Exit application
- `Tab` - Navigate between UI elements
- `Enter` - Activate selected element
- `Esc` - Go back to previous screen

### Main Dashboard
- `n` - New environment
- `r` - Refresh list
- `q` - Quit

### Environment Details
- `p` - Manage packages
- `d` - Configure Docker
- `a` - Launch AI tool
- `Esc` - Back to dashboard

## Color Scheme

The TUI uses a consistent color scheme:
- **Cyan** - Headers and titles
- **Green** - Success messages and confirmations
- **Yellow** - Warnings and in-progress status
- **Red** - Errors and validation failures
- **Primary** - Action buttons and highlights
- **Dim** - Secondary information

## Error Handling

The TUI provides inline error messages for:
- Invalid Python versions
- Missing project paths
- Invalid package specifications
- Docker generation failures
- AI tool availability issues

Errors are displayed in red status boxes with clear descriptions.

## Data Persistence

All configurations are stored in `.pyenv-cli/` directory:
- `configs.json` - Environment configurations
- `packages.json` - Package dependencies
- `docker.json` - Docker configurations
- `ai_sessions.json` - AI session history

## Tips & Best Practices

1. **Navigation** - Use keyboard shortcuts for faster navigation
2. **Batch Operations** - Add multiple packages before saving
3. **Context Switching** - The TUI maintains state when navigating screens
4. **Validation** - Pay attention to inline validation messages
5. **Session History** - All AI tool sessions are tracked for audit

## Troubleshooting

### TUI Won't Start
```bash
# Ensure Textual is installed
pip install textual>=0.47.0

# Try running directly
python -m pyenv_cli.tui
```

### Display Issues
```bash
# Check terminal compatibility
echo $TERM

# Recommended terminals:
# - iTerm2 (macOS)
# - Windows Terminal (Windows)
# - GNOME Terminal (Linux)
# - Alacritty (cross-platform)
```

### Package Not Found
```bash
# Reinstall in editable mode
cd pyenv-cli
pip install -e .
```

## Comparison: CLI vs TUI

| Feature | CLI | TUI |
|---------|-----|-----|
| **Interface** | Command arguments | Interactive forms |
| **Navigation** | Linear commands | Screen-based |
| **Feedback** | Text output | Real-time updates |
| **Batch Operations** | Multiple commands | Single session |
| **Learning Curve** | Memorize commands | Visual exploration |
| **Automation** | Script-friendly | Manual interaction |

**Use CLI when:**
- Scripting and automation
- CI/CD pipelines
- Quick one-off commands
- Remote/SSH sessions

**Use TUI when:**
- Initial setup and exploration
- Interactive configuration
- Visual environment management
- Learning the tool

## Examples

### Create Environment via TUI

1. Launch: `pyenv-tui`
2. Press `n` for new environment
3. Fill in:
   - Name: `myproject`
   - Python: `3.11`
   - Path: `.`
   - Docker: ✓
4. Click "Create"
5. View activation command

### Add Multiple Packages

1. Select environment from dashboard
2. Press `p` or click "Manage Packages"
3. Add packages:
   - `flask` (no version)
   - `requests` → `==2.31.0`
   - `pytest` → `>=7.0.0`
4. Click "Save All"
5. View generated requirements.txt path

### Configure Docker with Ports

1. Select environment
2. Press `d` or click "Configure Docker"
3. Ports: `8000,5432`
4. Command 1: `RUN apt-get update && apt-get install -y git`
5. Click "Generate Dockerfile"
6. View build instructions

## Architecture

The TUI is built on:
- **Textual** - Modern TUI framework
- **Rich** - Text formatting and styling
- **Same contracts** - Uses identical business logic as CLI
- **Reactive** - Event-driven architecture
- **Screens** - Navigation stack pattern

## Credits

Built with [Textual](https://textual.textualize.io/) by Will McGugan
Part of PyEnvCLI - Synthesized from AIM v1.4 specification

---

**Quick Start:** `pyenv-tui` → Press `n` → Fill form → Create!
