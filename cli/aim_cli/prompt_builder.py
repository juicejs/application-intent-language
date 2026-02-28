#!/usr/bin/env python3
"""
Prompt generation for AIM CLI
Build synthesis prompts for AI assistants
"""

import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional


BRAIN_URL = "https://intentmodel.dev/brain.md"


def build_synthesis_prompt(
    package_name: str,
    intent_files: List[Path],
    tech_stack: Dict[str, str],
    additional_context: str = ""
) -> str:
    """Build a formatted synthesis prompt for AI assistants"""

    # Build file list - use relative paths or just filenames
    file_paths = []
    for f in intent_files:
        try:
            # Try to get relative path from cwd
            rel_path = f.relative_to(Path.cwd())
            file_paths.append(f"  - {rel_path}")
        except ValueError:
            # If that fails, just use the filename with aim/ prefix
            file_paths.append(f"  - aim/{f.name}")

    file_list = "\n".join(file_paths)

    # Build tech stack section
    stack_items = []
    if tech_stack.get('frontend'):
        stack_items.append(f"  - Frontend: {tech_stack['frontend']}")
    if tech_stack.get('backend'):
        stack_items.append(f"  - Backend: {tech_stack['backend']}")
    if tech_stack.get('database'):
        stack_items.append(f"  - Database: {tech_stack['database']}")

    stack_section = "\n".join(stack_items)

    # Build additional context section
    context_section = ""
    if additional_context:
        context_section = f"\nAdditional Context:\n{additional_context}\n"

    # Build the complete prompt
    prompt = f"""Load your core system instructions from {BRAIN_URL}.
Initialize as the AIM Synthesizer and execute the Boot Sequence.

Package: {package_name}
Intent Files:
{file_list}

Tech Stack:
{stack_section}
{context_section}
Instructions:
Read the intent files in ./aim/ and synthesize production-ready code
following the AIM specification. Implement all requirements defined in
the INTENT, SCHEMA, FLOW, CONTRACT, and VIEW facets.

Start by understanding the intent structure, then generate a complete
implementation with proper error handling, validation, and tests."""

    return prompt


def interactive_prompt_builder(packages: List[str], current_config: Dict) -> Dict:
    """Interactive wizard to collect synthesis requirements"""
    print("\n🎯 AIM Synthesis Prompt Generator\n")

    # Select package
    if not packages:
        print("No packages found in aim/")
        return None

    print("Select package to synthesize:")
    for i, pkg in enumerate(packages, 1):
        print(f"  {i}. {pkg}")

    while True:
        try:
            choice = input(f"\nChoice [1-{len(packages)}]: ").strip()
            if not choice:
                return None
            idx = int(choice) - 1
            if 0 <= idx < len(packages):
                package_name = packages[idx]
                break
            else:
                print(f"Please enter a number between 1 and {len(packages)}")
        except (ValueError, KeyboardInterrupt):
            print("\nCancelled")
            return None

    # Tech stack configuration
    print("\nTech Stack Configuration:\n")

    stack = current_config.get('stack', {})

    frontend = input(f"Frontend framework [{stack.get('frontend', 'Next.js')}]: ").strip()
    if not frontend:
        frontend = stack.get('frontend', 'Next.js')

    backend = input(f"Backend framework [{stack.get('backend', 'Node.js')}]: ").strip()
    if not backend:
        backend = stack.get('backend', 'Node.js')

    database = input(f"Database [{stack.get('database', 'PostgreSQL')}]: ").strip()
    if not database:
        database = stack.get('database', 'PostgreSQL')

    # Additional context
    print("\nAdditional context (optional, press Enter to skip):")
    additional_context = input("> ").strip()

    return {
        'package': package_name,
        'stack': {
            'frontend': frontend,
            'backend': backend,
            'database': database
        },
        'context': additional_context
    }


def copy_to_clipboard(text: str) -> bool:
    """Copy text to clipboard - works on macOS, Linux, Windows"""
    try:
        if sys.platform == 'darwin':  # macOS
            proc = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
            proc.communicate(text.encode('utf-8'))
            return proc.returncode == 0
        elif sys.platform.startswith('linux'):  # Linux
            proc = subprocess.Popen(['xclip', '-selection', 'clipboard'],
                                  stdin=subprocess.PIPE)
            proc.communicate(text.encode('utf-8'))
            return proc.returncode == 0
        elif sys.platform == 'win32':  # Windows
            proc = subprocess.Popen(['clip'], stdin=subprocess.PIPE, shell=True)
            proc.communicate(text.encode('utf-8'))
            return proc.returncode == 0
    except FileNotFoundError:
        return False  # Clipboard utility not available
    except Exception:
        return False

    return False


def parse_stack_string(stack_str: str) -> Dict[str, str]:
    """Parse a comma-separated stack string like 'React,Node.js,PostgreSQL'"""
    parts = [p.strip() for p in stack_str.split(',')]

    stack = {}
    if len(parts) >= 1:
        stack['frontend'] = parts[0]
    if len(parts) >= 2:
        stack['backend'] = parts[1]
    if len(parts) >= 3:
        stack['database'] = parts[2]

    return stack
