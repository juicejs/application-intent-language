#!/bin/bash
# Quick start script for PyEnvCLI Terminal UI (Final Fixed Version)

echo "🚀 Starting PyEnvCLI Terminal UI..."
echo ""
echo "✨ Features:"
echo "  • Create Python virtual environments"
echo "  • Check & install Python versions"
echo "  • Search & add packages"
echo "  • 🔧 FIXED: Completely rewritten, no freezing!"
echo ""

# Check if installed
if ! command -v pyenv-tui &> /dev/null; then
    echo "⚠️  PyEnvCLI not installed. Installing now..."
    pip install -e .
    echo ""
fi

# Launch TUI
echo "✓ Launching Terminal UI..."
echo ""
pyenv-tui
