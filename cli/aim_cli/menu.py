#!/usr/bin/env python3
"""
Interactive menu system for AIM CLI
Provides guided workflows and configuration wizards

Copyright (c) 2026 Juice d.o.o (https://juice.com.hr)
Licensed under MIT License
"""

import sys
from pathlib import Path
from typing import Optional, Dict, List, Callable

from aim_cli import __version__
from aim_cli.cli import (
    Colors, print_success, print_error, print_info, print_warning,
    cmd_init, cmd_fetch, cmd_list, cmd_validate, cmd_info,
    fetch_registry, find_package, AIM_DIR, LOCK_FILE
)
from aim_cli.config import (
    load_config, save_config, get_config_path, DEFAULT_CONFIG
)
from aim_cli.prompt_builder import (
    build_synthesis_prompt, interactive_prompt_builder,
    copy_to_clipboard
)


def print_header(title: str) -> None:
    """Print a styled menu header"""
    border = "─" * (len(title) + 4)
    print(f"\n╭{border}╮")
    print(f"│  {Colors.BOLD}{title}{Colors.END}  │")
    print(f"╰{border}╯\n")


def get_menu_choice(prompt: str, valid_range: range) -> Optional[int]:
    """Get validated numeric input from user with Ctrl+C handling"""
    try:
        choice = input(prompt).strip()
        if not choice:
            return None

        num = int(choice)
        if num in valid_range:
            return num
        else:
            print_warning(f"Please enter a number between {valid_range.start} and {valid_range.stop - 1}")
            return get_menu_choice(prompt, valid_range)
    except ValueError:
        print_warning("Please enter a valid number")
        return get_menu_choice(prompt, valid_range)
    except (KeyboardInterrupt, EOFError):
        print("\n")
        return None


def show_main_menu() -> Optional[int]:
    """Display main menu and get user choice"""
    print_header("Sinth — Synthesize intent into reality")

    print(f"{Colors.CYAN}v{__version__}{Colors.END}\n")
    print("What would you like to do?\n")
    print(" 1. Initialize new project")
    print(" 2. Fetch package from registry")
    print(" 3. List installed packages")
    print(" 4. Generate synthesis prompt")
    print(" 5. Configure tech stack (wizard)")
    print(" 6. View/edit configuration")
    print(" 7. Validate intent files")
    print(" 8. Package information")
    print(" 9. Help")
    print(" 0. Exit\n")

    return get_menu_choice("Choice [0-9]: ", range(0, 10))


def menu_init() -> None:
    """Initialize new project with confirmation"""
    print_header("Initialize New Project")

    if AIM_DIR.exists():
        print_warning(f"{AIM_DIR}/ already exists")
        print_info("Project already initialized")
        input("\nPress Enter to continue...")
        return

    print_info(f"This will create the {AIM_DIR}/ directory")
    confirm = input("Continue? (y/n) [y]: ").strip().lower()

    if confirm in ('', 'y', 'yes'):
        class Args:
            pass
        cmd_init(Args())
        input("\nPress Enter to continue...")
    else:
        print_info("Cancelled")


def menu_fetch() -> None:
    """Fetch package with interactive selection"""
    print_header("Fetch Package from Registry")

    # Ensure aim/ directory exists
    if not AIM_DIR.exists():
        print_info(f"Creating {AIM_DIR}/ directory")
        AIM_DIR.mkdir(parents=True, exist_ok=True)

    # Fetch registry
    print_info("Fetching registry...")
    try:
        registry = fetch_registry()
    except Exception as e:
        print_error(f"Failed to fetch registry: {e}")
        input("\nPress Enter to continue...")
        return

    packages = registry.get('packages', [])
    if not packages:
        print_warning("No packages found in registry")
        input("\nPress Enter to continue...")
        return

    # Display package list
    print("\nAvailable packages:\n")
    for i, pkg in enumerate(packages, 1):
        name = pkg.get('name', 'unknown')
        version = pkg.get('version', 'unknown')
        description = pkg.get('description', '')
        print(f"  {i}. {name} (v{version})")
        if description:
            print(f"     {Colors.CYAN}→{Colors.END} {description}")
    print(f"  0. Back to main menu\n")

    # Get selection
    choice = get_menu_choice(f"Choose package [0-{len(packages)}]: ",
                            range(0, len(packages) + 1))
    if choice == 0 or choice is None:
        return

    # Fetch selected package
    selected_pkg = packages[choice - 1]

    class Args:
        package = selected_pkg.get('name')

    print()
    try:
        cmd_fetch(Args())
    except Exception as e:
        print_error(f"Failed to fetch package: {e}")

    input("\nPress Enter to continue...")


def menu_list() -> None:
    """List installed packages"""
    print_header("Installed Packages")

    class Args:
        pass

    cmd_list(Args())
    input("Press Enter to continue...")


def menu_synth() -> None:
    """Synthesis prompt generation submenu"""
    print_header("Generate Synthesis Prompt")

    if not AIM_DIR.exists():
        print_warning(f"No {AIM_DIR}/ directory found")
        print_info("Initialize project first (option 1)")
        input("\nPress Enter to continue...")
        return

    # Get list of packages
    intent_files = list(AIM_DIR.glob("*.intent"))
    if not intent_files:
        print_warning("No packages installed")
        print_info("Fetch a package first (option 2)")
        input("\nPress Enter to continue...")
        return

    # Extract package names
    packages = []
    for f in intent_files:
        # Remove .intent extension
        pkg_name = f.stem
        packages.append(pkg_name)

    print("\n 1. Quick synthesis (use config settings)")
    print(" 2. Interactive prompt builder")
    print(" 3. List installed packages")
    print(" 0. Back to main menu\n")

    choice = get_menu_choice("Choice [0-3]: ", range(0, 4))

    if choice == 0 or choice is None:
        return
    elif choice == 1:
        # Quick synth
        print("\nSelect package:\n")
        for i, pkg in enumerate(packages, 1):
            print(f"  {i}. {pkg}")
        print()

        pkg_choice = get_menu_choice(f"Choice [1-{len(packages)}]: ",
                                    range(1, len(packages) + 1))
        if pkg_choice is None:
            return

        package_name = packages[pkg_choice - 1]
        config = load_config()

        # Find intent files
        intent_files_list = list(AIM_DIR.glob(f"*{package_name}*.intent"))

        # Build and display prompt
        prompt = build_synthesis_prompt(
            package_name=package_name,
            intent_files=intent_files_list,
            tech_stack=config.get('stack', {}),
            additional_context=''
        )

        print()
        print_success("Generated synthesis prompt:")
        print()
        print(prompt)
        print()

        # Copy to clipboard
        if copy_to_clipboard(prompt):
            print_success("✓ Copied to clipboard!")
        else:
            print_warning("Could not copy to clipboard")

        input("\nPress Enter to continue...")

    elif choice == 2:
        # Interactive builder
        config = load_config()
        prompt_data = interactive_prompt_builder(packages, config)

        if prompt_data:
            # Find intent files
            intent_files_list = list(AIM_DIR.glob(f"*{prompt_data['package']}*.intent"))

            # Build prompt
            prompt = build_synthesis_prompt(
                package_name=prompt_data['package'],
                intent_files=intent_files_list,
                tech_stack=prompt_data['stack'],
                additional_context=prompt_data.get('context', '')
            )

            print()
            print_success("Generated synthesis prompt:")
            print()
            print(prompt)
            print()

            # Copy to clipboard
            if copy_to_clipboard(prompt):
                print_success("✓ Copied to clipboard!")
            else:
                print_warning("Could not copy to clipboard")

        input("\nPress Enter to continue...")

    elif choice == 3:
        # List packages
        menu_list()


def menu_config_wizard() -> None:
    """Interactive configuration wizard - step-by-step setup"""
    print_header("Configuration Wizard")

    config = load_config()

    print("Let's configure your tech stack step by step.\n")
    print_info("Press Enter to keep current value, or type a new value\n")

    # Step 1: Frontend
    print(f"{Colors.BOLD}Step 1/5: Frontend Framework{Colors.END}")
    print(f"Current: {config['stack']['frontend']}\n")
    print("Common options:")
    print("  1. Next.js")
    print("  2. React")
    print("  3. Vue.js")
    print("  4. Svelte")
    print("  5. Angular")
    print("  6. Custom (enter manually)\n")

    try:
        choice_input = input("Choice [1-6] or Enter to keep current: ").strip()
        if not choice_input:
            frontend = config['stack']['frontend']
        else:
            frontend_choice = int(choice_input)
            if frontend_choice == 1:
                frontend = "Next.js"
            elif frontend_choice == 2:
                frontend = "React"
            elif frontend_choice == 3:
                frontend = "Vue.js"
            elif frontend_choice == 4:
                frontend = "Svelte"
            elif frontend_choice == 5:
                frontend = "Angular"
            elif frontend_choice == 6:
                frontend = input("Enter frontend framework: ").strip()
            else:
                frontend = config['stack']['frontend']
    except (ValueError, KeyboardInterrupt):
        frontend = config['stack']['frontend']

    # Step 2: Backend
    print(f"\n{Colors.BOLD}Step 2/5: Backend Framework{Colors.END}")
    print(f"Current: {config['stack']['backend']}\n")
    print("Common options:")
    print("  1. Node.js")
    print("  2. Express")
    print("  3. FastAPI")
    print("  4. Django")
    print("  5. Spring Boot")
    print("  6. Custom (enter manually)\n")

    try:
        choice_input = input("Choice [1-6] or Enter to keep current: ").strip()
        if not choice_input:
            backend = config['stack']['backend']
        else:
            backend_choice = int(choice_input)
            if backend_choice == 1:
                backend = "Node.js"
            elif backend_choice == 2:
                backend = "Express"
            elif backend_choice == 3:
                backend = "FastAPI"
            elif backend_choice == 4:
                backend = "Django"
            elif backend_choice == 5:
                backend = "Spring Boot"
            elif backend_choice == 6:
                backend = input("Enter backend framework: ").strip()
            else:
                backend = config['stack']['backend']
    except (ValueError, KeyboardInterrupt):
        backend = config['stack']['backend']

    # Step 3: Database
    print(f"\n{Colors.BOLD}Step 3/5: Database{Colors.END}")
    print(f"Current: {config['stack']['database']}\n")
    print("Common options:")
    print("  1. PostgreSQL")
    print("  2. MySQL")
    print("  3. MongoDB")
    print("  4. SQLite")
    print("  5. Redis")
    print("  6. Custom (enter manually)\n")

    try:
        choice_input = input("Choice [1-6] or Enter to keep current: ").strip()
        if not choice_input:
            database = config['stack']['database']
        else:
            database_choice = int(choice_input)
            if database_choice == 1:
                database = "PostgreSQL"
            elif database_choice == 2:
                database = "MySQL"
            elif database_choice == 3:
                database = "MongoDB"
            elif database_choice == 4:
                database = "SQLite"
            elif database_choice == 5:
                database = "Redis"
            elif database_choice == 6:
                database = input("Enter database: ").strip()
            else:
                database = config['stack']['database']
    except (ValueError, KeyboardInterrupt):
        database = config['stack']['database']

    # Step 4: Registry URL (advanced)
    print(f"\n{Colors.BOLD}Step 4/5: Registry URL{Colors.END}")
    print(f"Current: {config['registry']}\n")
    registry = input(f"Registry URL [{config['registry']}]: ").strip()
    if not registry:
        registry = config['registry']

    # Step 5: Output directory
    print(f"\n{Colors.BOLD}Step 5/5: Output Directory{Colors.END}")
    print(f"Current: {config['outputDir']}\n")
    output_dir = input(f"Output directory [{config['outputDir']}]: ").strip()
    if not output_dir:
        output_dir = config['outputDir']

    # Review configuration
    print(f"\n{Colors.BOLD}Review Configuration{Colors.END}\n")
    print(f"  Frontend:  {frontend}")
    print(f"  Backend:   {backend}")
    print(f"  Database:  {database}")
    print(f"  Registry:  {registry}")
    print(f"  Output:    {output_dir}\n")

    confirm = input("Save this configuration? (y/n) [y]: ").strip().lower()

    if confirm in ('', 'y', 'yes'):
        new_config = {
            "version": "1.0",
            "stack": {
                "frontend": frontend,
                "backend": backend,
                "database": database
            },
            "registry": registry,
            "outputDir": output_dir
        }

        try:
            save_config(new_config)
            print_success(f"✓ Configuration saved to {get_config_path()}")
        except Exception as e:
            print_error(f"Failed to save configuration: {e}")
    else:
        print_info("Configuration not saved")

    input("\nPress Enter to continue...")


def menu_config_view() -> None:
    """View and quick edit configuration"""
    print_header("View/Edit Configuration")

    config_path = get_config_path()

    if not config_path.exists():
        print_warning("No configuration file found")
        print_info("Use option 5 (Configure tech stack) to create one")
        input("\nPress Enter to continue...")
        return

    try:
        config = load_config()
    except Exception as e:
        print_error(f"Failed to load configuration: {e}")
        input("\nPress Enter to continue...")
        return

    # Display current config
    print(f"{Colors.BOLD}Current Configuration:{Colors.END}\n")
    print(f"  Config file: {config_path}")
    print(f"  Version:     {config.get('version', 'unknown')}")
    print(f"  Frontend:    {config['stack']['frontend']}")
    print(f"  Backend:     {config['stack']['backend']}")
    print(f"  Database:    {config['stack']['database']}")
    print(f"  Registry:    {config['registry']}")
    print(f"  Output Dir:  {config['outputDir']}\n")

    print(" 1. Edit configuration (wizard)")
    print(" 2. Reset to defaults")
    print(" 0. Back to main menu\n")

    choice = get_menu_choice("Choice [0-2]: ", range(0, 3))

    if choice == 1:
        menu_config_wizard()
    elif choice == 2:
        confirm = input("Reset to default configuration? (y/n) [n]: ").strip().lower()
        if confirm == 'y':
            try:
                save_config(DEFAULT_CONFIG)
                print_success("✓ Configuration reset to defaults")
            except Exception as e:
                print_error(f"Failed to reset configuration: {e}")
            input("\nPress Enter to continue...")


def menu_validate() -> None:
    """Validate intent files"""
    print_header("Validate Intent Files")

    class Args:
        pass

    cmd_validate(Args())
    input("\nPress Enter to continue...")


def menu_info() -> None:
    """Show package information with interactive selection"""
    print_header("Package Information")

    # Fetch registry
    print_info("Fetching registry...")
    try:
        registry = fetch_registry()
    except Exception as e:
        print_error(f"Failed to fetch registry: {e}")
        input("\nPress Enter to continue...")
        return

    packages = registry.get('packages', [])
    if not packages:
        print_warning("No packages found in registry")
        input("\nPress Enter to continue...")
        return

    # Display package list
    print("\nAvailable packages:\n")
    for i, pkg in enumerate(packages, 1):
        name = pkg.get('name', 'unknown')
        version = pkg.get('version', 'unknown')
        print(f"  {i}. {name} (v{version})")
    print(f"  0. Back to main menu\n")

    # Get selection
    choice = get_menu_choice(f"Choose package [0-{len(packages)}]: ",
                            range(0, len(packages) + 1))
    if choice == 0 or choice is None:
        return

    # Show selected package info
    selected_pkg = packages[choice - 1]

    class Args:
        package = selected_pkg.get('name')

    print()
    try:
        cmd_info(Args())
    except Exception as e:
        print_error(f"Failed to get package info: {e}")

    input("\nPress Enter to continue...")


def menu_help() -> None:
    """Display help and quick reference"""
    print_header("Help & Quick Reference")

    print(f"{Colors.BOLD}Sinth — the CLI for AIM{Colors.END}\n")
    print("Sinth helps you fetch, manage, and synthesize intent-based packages.\n")

    print(f"{Colors.BOLD}Getting Started:{Colors.END}\n")
    print("  1. Initialize a project:     sinth init")
    print("  2. Fetch a package:          sinth fetch weather")
    print("  3. Generate synthesis:       sinth synth weather\n")

    print(f"{Colors.BOLD}Common Commands:{Colors.END}\n")
    print("  sinth                        Interactive menu (this menu)")
    print("  sinth init                   Initialize new project")
    print("  sinth fetch <package>        Fetch package from registry")
    print("  sinth list                   List installed packages")
    print("  sinth synth <package>        Generate synthesis prompt")
    print("  sinth synth --interactive    Interactive prompt builder")
    print("  sinth validate               Validate intent files")
    print("  sinth info <package>         Show package information")
    print("  sinth config init            Create configuration file")
    print("  sinth config list            Show configuration\n")

    print(f"{Colors.BOLD}Configuration:{Colors.END}\n")
    print("  Configuration is stored in aim.config.json")
    print("  Use the wizard (option 5) for guided setup")
    print("  Or use: sinth config set stack.frontend React\n")

    print(f"{Colors.BOLD}Need More Help?{Colors.END}\n")
    print("  Documentation: https://intentmodel.dev")
    print("  Registry:      https://intentmodel.dev/registry-files/index.json\n")

    input("Press Enter to continue...")


# Menu handler dispatch table
MENU_HANDLERS: Dict[int, Callable] = {
    1: menu_init,
    2: menu_fetch,
    3: menu_list,
    4: menu_synth,
    5: menu_config_wizard,
    6: menu_config_view,
    7: menu_validate,
    8: menu_info,
    9: menu_help,
}


def run_interactive_menu() -> None:
    """Main interactive menu loop"""
    while True:
        try:
            choice = show_main_menu()

            if choice == 0 or choice is None:
                print_info("Goodbye!")
                break

            handler = MENU_HANDLERS.get(choice)
            if handler:
                handler()
            else:
                print_warning("Invalid choice")

        except KeyboardInterrupt:
            print("\n")
            print_info("Goodbye!")
            break
        except Exception as e:
            print_error(f"An error occurred: {e}")
            input("\nPress Enter to continue...")
