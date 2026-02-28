# Sinth — the CLI for AIM

**Synthesize intent into reality.**

Simple Python CLI for managing AIM packages from the registry.

## Installation

### Option 1: pip (Recommended)

```bash
pip install sinth
```

Then use directly:
```bash
sinth fetch weather
sinth list
sinth validate
```

### Option 2: From source

```bash
git clone https://github.com/juicejs/application-intent-language.git
cd application-intent-language
pip install -e .
```

### Option 3: Standalone script

```bash
curl -O https://raw.githubusercontent.com/juicejs/application-intent-language/master/cli/aim_cli/cli.py
python3 cli.py fetch weather
```

## Requirements

- Python 3.6+ (pre-installed on macOS/Linux, available on Windows)
- No external dependencies (uses only Python stdlib)

## Quick Start

### Interactive Menu (Recommended for New Users)

Simply run `sinth` without arguments to launch the interactive menu:

```bash
sinth
```

This will display:
```
╭─────────────────────────────────────────────╮
│  Sinth — Synthesize intent into reality     │
╰─────────────────────────────────────────────╯

What would you like to do?

 1. Initialize new project
 2. Fetch package from registry
 3. List installed packages
 4. Generate synthesis prompt
 5. Configure tech stack (wizard)
 6. View/edit configuration
 7. Validate intent files
 8. Package information
 9. Help
 0. Exit

Choice [0-9]:
```

The interactive menu provides:
- **Guided workflows** - Step-by-step instructions for each task
- **Configuration wizard** - Easy tech stack setup with common presets
- **Package browsing** - View and select packages from the registry
- **Smart defaults** - Loads values from existing configuration

### Command Line Interface

For power users and automation, all functionality is available via CLI commands:

```bash
# Initialize a project
sinth init

# Fetch a package
sinth fetch weather

# List installed packages
sinth list

# Validate intent files
sinth validate

# Show package info
sinth info weather

# Configure tech stack
sinth config set stack.frontend "React"
sinth config set stack.backend "FastAPI"

# Generate synthesis prompt
sinth synth weather
```

## Interactive Menu

### Main Menu

Running `sinth` without arguments launches an interactive menu system that provides guided access to all CLI features.

**Navigation:**
- Enter a number (0-9) to select an option
- Press Ctrl+C to return to previous menu or exit
- Follow on-screen prompts for each operation

**Menu Options:**

1. **Initialize new project** - Creates the `aim/` directory with confirmation
2. **Fetch package from registry** - Browse and select packages from the live registry
3. **List installed packages** - View all packages in your `aim/` directory
4. **Generate synthesis prompt** - Quick or interactive prompt generation
5. **Configure tech stack (wizard)** - Step-by-step configuration setup
6. **View/edit configuration** - Display current config and make changes
7. **Validate intent files** - Check all intent files for errors
8. **Package information** - View detailed info for any registry package
9. **Help** - Quick reference and command examples

### Configuration Wizard

The configuration wizard (option 5 in main menu) provides an interactive way to set up your tech stack:

```
╭─────────────────────────────────────────────╮
│  Configuration Wizard                       │
╰─────────────────────────────────────────────╯

Step 1/5: Frontend Framework
Current: Next.js

Common options:
  1. Next.js
  2. React
  3. Vue.js
  4. Svelte
  5. Angular
  6. Custom (enter manually)

Choice [1-6] or Enter to keep current:
```

**Features:**
- Step-by-step guided setup
- Common framework presets
- Custom value input option
- Shows current values as defaults
- Configuration review before saving
- Creates/updates `aim.config.json`

**Configurable Settings:**
- Frontend framework (Next.js, React, Vue.js, etc.)
- Backend framework (Node.js, Express, FastAPI, etc.)
- Database (PostgreSQL, MySQL, MongoDB, etc.)
- Registry URL (advanced)
- Output directory (advanced)

### Synthesis Submenu

The synthesis menu (option 4 in main menu) offers two modes:

**Quick Synthesis:**
- Select a package from numbered list
- Uses configuration from `aim.config.json`
- Generates and copies prompt to clipboard

**Interactive Builder:**
- Select package
- Customize tech stack for this synthesis
- Add optional context notes
- Generates and copies prompt to clipboard

## Commands

### `sinth`
Launch interactive menu (new in this release).

```bash
sinth
```

This is the recommended entry point for new users and configuration tasks.

### `sinth init`
Initialize AIM project (creates `aim/` directory).

```bash
sinth init
```

### `sinth fetch <package>`
Fetch a package from the registry and save to `aim/` folder.

```bash
sinth fetch weather
sinth fetch game.snake
```

Creates:
- `aim/weather.intent` (or similar)
- `aim.lock` (package lock file)

### `sinth list`
List all installed packages.

```bash
sinth list
```

Shows:
- Intent files in `aim/` directory
- Package versions from lock file

### `sinth validate`
Validate local intent files.

```bash
sinth validate
```

Checks:
- AIM header presence
- Header format (feature#facet@version)
- File encoding

### `sinth info <package>`
Show information about a package.

```bash
sinth info weather
```

Shows:
- Package name and version
- Entry file path
- Installation status

### `sinth config`
Manage project configuration.

```bash
# Initialize config file
sinth config init

# Set config values
sinth config set stack.frontend "React"
sinth config set stack.backend "Node.js"
sinth config set stack.database "PostgreSQL"

# Get config value
sinth config get stack.frontend

# List all config
sinth config list
```

The config is stored in `aim.config.json` in your project root:

```json
{
  "version": "1.0",
  "stack": {
    "frontend": "Next.js",
    "backend": "Node.js",
    "database": "PostgreSQL"
  },
  "registry": "https://intentmodel.dev/registry/index.json",
  "outputDir": "aim"
}
```

### `sinth synth <package>`
Generate synthesis prompts for AI assistants.

```bash
# Generate prompt (auto-copies to clipboard)
sinth synth weather

# Generate with custom tech stack
sinth synth weather --stack "React,Node.js,MongoDB"

# Interactive mode
sinth synth --interactive

# Display without copying to clipboard
sinth synth weather --no-copy

# List available packages
sinth synth --list
```

The command generates a formatted prompt that:
- References the AIM brain.md instructions
- Includes package and file information
- Specifies your tech stack
- Provides clear synthesis instructions
- Automatically copies to clipboard (by default)

**Example output:**
```
Load your core system instructions from https://intentmodel.dev/brain.md.
Initialize as the AIM Synthesizer and execute the Boot Sequence.

Package: weather
Intent Files:
  - aim/weather.intent

Tech Stack:
  - Frontend: Next.js
  - Backend: Node.js
  - Database: PostgreSQL

Instructions:
Read the intent files in ./aim/ and synthesize production-ready code
following the AIM specification. Implement all requirements defined in
the INTENT, SCHEMA, FLOW, CONTRACT, and VIEW facets.
```

**Interactive Mode:**
```bash
$ sinth synth --interactive

🎯 AIM Synthesis Prompt Generator

Select package to synthesize:
  1. weather (v1.4)
  2. game.snake (v1.4)

Choice [1-2]: 1

Tech Stack Configuration:

Frontend framework [Next.js]: React
Backend framework [Node.js]:
Database [PostgreSQL]:

✓ Generated prompt (42 lines)
✓ Copied to clipboard!
```

## Directory Structure

After fetching packages and configuring:

```
your-project/
├── aim/                 # AIM source files
│   ├── weather.intent
│   └── game.snake.intent
├── aim.lock            # Package lock file
└── aim.config.json     # Project config (optional)
```

## Lock File

The `aim.lock` file tracks installed packages:

```json
{
  "weather": {
    "version": "1.4",
    "entry": "registry/packages/weather/weather.intent"
  }
}
```

## For AI Agents

When synthesizing AIM packages, AI agents should:

1. **Fetch package**: `sinth fetch <package>`
2. **Validate**: `sinth validate`
3. **Read local files**: All intent files are in `aim/` directory
4. **Generate prompt**: `sinth synth <package>` (automatically creates a structured prompt)
5. **Synthesize**: Generate code based on the prompt and intent files

The CLI ensures consistent package structure and handles registry fetching automatically.

### Config File for AI Agents

The `aim.config.json` file is designed to be readable by AI agents. It stores project preferences like tech stack, which helps agents understand your project context without requiring explicit configuration each time.

**Human workflow:**
```bash
sinth config set stack.frontend "React"
sinth synth weather  # Uses React from config
```

**AI agent workflow:**
```bash
# AI can read aim.config.json directly
cat aim.config.json  # See project preferences
sinth synth weather  # Generate prompt with config
```

## Troubleshooting

**"No aim/ directory found"**
- Run `sinth init` first

**"Package not found"**
- Check available packages: `sinth list`
- Verify package name matches registry

**"Failed to fetch registry"**
- Check internet connection
- Verify https://intentmodel.dev is accessible

**"Could not copy to clipboard"**
- Install clipboard utility:
  - macOS: `pbcopy` (pre-installed)
  - Linux: `sudo apt-get install xclip`
  - Windows: `clip` (pre-installed)
- Or use `--no-copy` flag and copy manually

## Features

### ✅ Current
- **Interactive menu system** - Guided workflows for all operations
- **Configuration wizard** - Step-by-step tech stack setup
- Package management (init, fetch, list, validate, info)
- Configuration system (config init, get, set, list)
- Synthesis prompt generation (synth)
- Interactive prompt builder
- Clipboard integration
- Tech stack configuration
- AI-readable config files

### 🚧 Future
- `sinth update <package>` - Update installed packages
- `sinth search <query>` - Search registry
- `sinth remove <package>` - Remove packages
- `sinth sync` - Sync from aim.lock
- Version pinning support
- `sinth synth --watch` - Watch for changes and regenerate
- `sinth synth --template <name>` - Custom prompt templates
- Multiple package synthesis
