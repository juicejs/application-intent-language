# 🚀 PyEnvCLI Terminal UI - Quick Start Guide

## Installation (One-Time Setup)

```bash
cd /Users/filipjovanovic/Desktop/application-intent-model/pyenv-cli
pip install -e .
```

This installs two commands:
- `pyenv-cli` - Traditional CLI
- `pyenv-tui` - Terminal UI (recommended)

## 🎯 How to Start the TUI

### Method 1: Direct Command (Simplest)

```bash
pyenv-tui
```

### Method 2: Using the Start Script

```bash
cd /Users/filipjovanovic/Desktop/application-intent-model/pyenv-cli
./START_TUI.sh
```

### Method 3: Python Module

```bash
python -m pyenv_cli.tui
```

## 🖥️ What You'll See

When launched, the TUI displays:

```
╭────────────────────────────────────────────────╮
│      🐍 PyEnvCLI Terminal UI                   │
│   Manage Python virtual environments           │
├────────────────────────────────────────────────┤
│  ID      Name     Python  Docker  Created      │
│  abc123  myenv    3.11    ✓       2024-03-04   │
│  def456  webapp   3.12    ✗       2024-03-03   │
├────────────────────────────────────────────────┤
│  [New Environment] [Refresh] [Quit]            │
╰────────────────────────────────────────────────╯
```

## ⌨️ First Steps

### Create Your First Environment

1. Press `n` (or click "New Environment")
2. Fill in the form:
   - **Name:** `myenv`
   - **Python:** `3.11`
   - **Path:** `.` (current directory)
   - **Docker:** Check if needed
3. Click "Create" button
4. Copy the activation command shown

### Navigate the Interface

- **Arrow keys** - Move between elements
- **Tab** - Next field
- **Enter** - Activate/Submit
- **Esc** - Go back
- **Mouse** - Click buttons and select items

### Explore an Environment

1. Use arrows to select an environment
2. Press `Enter` to view details
3. From details screen:
   - Press `p` - Manage packages
   - Press `d` - Configure Docker
   - Press `a` - Launch AI assistant

## 📦 Add Packages Example

1. Create or select an environment
2. Press `p` for packages
3. Add packages:
   ```
   Package: flask
   Version: (leave empty for latest)
   [Add Package]

   Package: requests
   Version: ==2.31.0
   [Add Package]

   [Save All]
   ```

## 🐳 Generate Dockerfile Example

1. Select environment
2. Press `d` for Docker
3. Configure:
   ```
   Ports: 8000,5432
   Command 1: RUN apt-get update
   [Generate Dockerfile]
   ```

## 🤖 Launch AI Assistant

1. Select environment
2. Press `a` for AI tools
3. Choose tool (e.g., Claude Code)
4. Enter prompt: "Help me structure this project"
5. Follow instructions to launch

## ❌ Exit the TUI

- Press `q` on main screen
- Or press `Ctrl+C`

## 🔧 Troubleshooting

### TUI Won't Start

```bash
# Ensure Textual is installed
pip install textual>=0.47.0

# Reinstall package
cd /Users/filipjovanovic/Desktop/application-intent-model/pyenv-cli
pip install -e . --force-reinstall
```

### Command Not Found

```bash
# Check installation
pip show pyenv-cli

# If not found, reinstall
pip install -e .
```

### Display Issues

The TUI works best with modern terminals:
- **macOS:** iTerm2 or Terminal.app
- **Windows:** Windows Terminal
- **Linux:** GNOME Terminal, Alacritty

## 📚 Full Documentation

- **TUI Guide:** [TUI_GUIDE.md](TUI_GUIDE.md) - Complete interface reference
- **README:** [README.md](README.md) - Full project documentation

## 🎬 Video Tutorial (Text Version)

### Complete Workflow in 5 Minutes

```bash
# 1. Launch TUI
pyenv-tui

# You'll see the main dashboard

# 2. Press 'n' to create new environment
# Fill in:
#   Name: demo-project
#   Python: 3.11
#   Docker: ✓

# 3. Environment created! Copy activation:
#   source demo-project/bin/activate

# 4. Press Esc to return to dashboard

# 5. Select your new environment and press Enter

# 6. Press 'p' to add packages
# Add:
#   - flask (no version)
#   - pytest >=7.0.0
# Click "Save All"

# 7. Press Esc, then 'd' for Docker
# Ports: 5000
# Click "Generate Dockerfile"

# 8. Done! Press 'q' to exit
```

## 💡 Pro Tips

1. **Keyboard Shortcuts** - Learn `n`, `p`, `d`, `a`, `q` for fast navigation
2. **Tab Navigation** - Use Tab to move between form fields
3. **Mouse Support** - Click anywhere for quick access
4. **Partial IDs** - Environment IDs show first 8 characters (enough for selection)
5. **Real-time Validation** - Watch for red error messages as you type

## 🆘 Need Help?

While in the TUI:
- Look at the **Footer** for available keyboard shortcuts
- Status messages appear in **yellow** (info) or **red** (error)
- All actions are **reversible** - experiment freely!

## ✅ Next Steps

After creating your environment:

1. **Activate it:**
   ```bash
   source <env-name>/bin/activate
   ```

2. **Verify packages:**
   ```bash
   pip list
   ```

3. **Build Docker image (if generated):**
   ```bash
   docker build -t myapp .
   ```

4. **Start coding!**

---

**Ready?** Run this now:

```bash
pyenv-tui
```

🎉 Enjoy your new Python environment manager!
