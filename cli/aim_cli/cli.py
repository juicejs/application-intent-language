#!/usr/bin/env python3
"""
Sinth — the CLI for AIM. Synthesize intent into reality.
Fetch and manage AIM packages from the registry.
"""

import argparse
import json
import sys
import urllib.request
import urllib.error
from pathlib import Path
from typing import Optional, Dict, List

from aim_cli.config import (
    load_config, save_config, init_config, get_config_path,
    get_config_value, set_config_value
)
from aim_cli.prompt_builder import (
    build_synthesis_prompt, interactive_prompt_builder,
    copy_to_clipboard, parse_stack_string
)

# Configuration
REGISTRY_URL = "https://intentmodel.dev/registry-files/index.json"
AIM_DIR = Path("aim")
LOCK_FILE = Path("aim.lock")


class Colors:
    """ANSI color codes for terminal output"""
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_success(msg: str):
    print(f"{Colors.GREEN}✓{Colors.END} {msg}")


def print_error(msg: str):
    print(f"{Colors.RED}✗{Colors.END} {msg}", file=sys.stderr)


def print_info(msg: str):
    print(f"{Colors.CYAN}→{Colors.END} {msg}")


def print_warning(msg: str):
    print(f"{Colors.YELLOW}⚠{Colors.END} {msg}")


def fetch_registry() -> Dict:
    """Fetch the registry index from the remote server"""
    try:
        print_info(f"Fetching registry from {REGISTRY_URL}")
        with urllib.request.urlopen(REGISTRY_URL, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            print_success("Registry fetched successfully")
            return data
    except urllib.error.URLError as e:
        print_error(f"Failed to fetch registry: {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print_error(f"Failed to parse registry JSON: {e}")
        sys.exit(1)


def find_package(registry: Dict, package_name: str) -> Optional[Dict]:
    """Find a package in the registry by name"""
    packages = registry.get('packages', [])
    for pkg in packages:
        if pkg.get('name') == package_name:
            return pkg
    return None


def fetch_file(url: str) -> str:
    """Fetch a file from a URL and return its content"""
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            return response.read().decode('utf-8')
    except urllib.error.URLError as e:
        raise Exception(f"Failed to fetch {url}: {e}")


def resolve_package_urls(entry_path: str) -> List[str]:
    """Convert registry entry path to full URLs"""
    base_url = "https://intentmodel.dev"
    # entry_path is like "registry/packages/weather/weather.intent"
    # Convert to "registry-files/packages/weather/weather.intent"
    url_path = entry_path.replace("registry/", "registry-files/", 1)
    return [f"{base_url}/{url_path}"]


def cmd_init(args):
    """Initialize AIM project (create aim/ directory)"""
    if AIM_DIR.exists():
        print_warning(f"{AIM_DIR}/ already exists")
        return

    AIM_DIR.mkdir(parents=True, exist_ok=True)
    print_success(f"Initialized AIM project in {AIM_DIR}/")
    print_info("Use 'aim fetch <package>' to install packages")


def cmd_fetch(args):
    """Fetch a package from the registry"""
    package_name = args.package

    # Ensure aim/ directory exists
    if not AIM_DIR.exists():
        print_info("Creating aim/ directory")
        AIM_DIR.mkdir(parents=True, exist_ok=True)

    # Fetch registry
    registry = fetch_registry()

    # Find package
    pkg = find_package(registry, package_name)
    if not pkg:
        print_error(f"Package '{package_name}' not found in registry")
        available = [p.get('name') for p in registry.get('packages', [])]
        print_info(f"Available packages: {', '.join(available)}")
        sys.exit(1)

    print_info(f"Found package: {pkg['name']} v{pkg['version']}")

    # Get package URLs
    urls = resolve_package_urls(pkg['entry'])

    # Fetch and save files
    for url in urls:
        try:
            print_info(f"Fetching {url}")
            content = fetch_file(url)

            # Extract filename from URL
            filename = url.split('/')[-1]
            dest_path = AIM_DIR / filename

            # Write file
            dest_path.write_text(content, encoding='utf-8')
            print_success(f"Saved {dest_path}")

        except Exception as e:
            print_error(str(e))
            sys.exit(1)

    # Update lock file
    update_lock_file(pkg)

    print_success(f"Package '{package_name}' installed successfully")


def cmd_list(args):
    """List installed packages"""
    if not AIM_DIR.exists():
        print_warning("No aim/ directory found. Run 'aim init' first.")
        return

    intent_files = list(AIM_DIR.glob("*.intent"))

    if not intent_files:
        print_info("No packages installed")
        return

    print(f"\n{Colors.BOLD}Installed packages:{Colors.END}")
    for intent_file in sorted(intent_files):
        # Try to extract package info from header
        try:
            content = intent_file.read_text(encoding='utf-8')
            first_line = content.split('\n')[0].strip()
            if first_line.startswith('AIM:'):
                header = first_line.replace('AIM:', '').strip()
                print(f"  {Colors.CYAN}•{Colors.END} {intent_file.name} ({header})")
            else:
                print(f"  {Colors.CYAN}•{Colors.END} {intent_file.name}")
        except Exception:
            print(f"  {Colors.CYAN}•{Colors.END} {intent_file.name}")

    print()

    # Show lock file if exists
    if LOCK_FILE.exists():
        try:
            lock_data = json.loads(LOCK_FILE.read_text())
            print(f"{Colors.BOLD}Lock file:{Colors.END}")
            for pkg_name, pkg_info in lock_data.items():
                print(f"  {Colors.CYAN}•{Colors.END} {pkg_name} v{pkg_info.get('version')}")
            print()
        except Exception:
            pass


def cmd_validate(args):
    """Validate local intent files"""
    if not AIM_DIR.exists():
        print_warning("No aim/ directory found")
        return

    intent_files = list(AIM_DIR.glob("*.intent"))

    if not intent_files:
        print_warning("No .intent files found")
        return

    print_info("Validating intent files...")
    valid_count = 0
    invalid_count = 0

    for intent_file in intent_files:
        try:
            content = intent_file.read_text(encoding='utf-8')
            lines = content.split('\n')

            # Check for AIM header
            if not lines or not lines[0].strip().startswith('AIM:'):
                print_error(f"{intent_file.name}: Missing AIM header")
                invalid_count += 1
                continue

            # Basic header validation
            header = lines[0].strip()
            if '#' not in header or '@' not in header:
                print_error(f"{intent_file.name}: Invalid AIM header format")
                invalid_count += 1
                continue

            print_success(f"{intent_file.name}: Valid")
            valid_count += 1

        except Exception as e:
            print_error(f"{intent_file.name}: {e}")
            invalid_count += 1

    print()
    print_info(f"Validation complete: {valid_count} valid, {invalid_count} invalid")

    if invalid_count > 0:
        sys.exit(1)


def update_lock_file(pkg: Dict):
    """Update the aim.lock file with package info"""
    lock_data = {}

    # Read existing lock file
    if LOCK_FILE.exists():
        try:
            lock_data = json.loads(LOCK_FILE.read_text())
        except Exception:
            pass

    # Update with new package
    lock_data[pkg['name']] = {
        'version': pkg['version'],
        'entry': pkg['entry']
    }

    # Write lock file
    LOCK_FILE.write_text(json.dumps(lock_data, indent=2), encoding='utf-8')


def cmd_info(args):
    """Show information about a package"""
    package_name = args.package

    # Fetch registry
    registry = fetch_registry()

    # Find package
    pkg = find_package(registry, package_name)
    if not pkg:
        print_error(f"Package '{package_name}' not found in registry")
        sys.exit(1)

    print(f"\n{Colors.BOLD}{pkg['name']}{Colors.END}")
    print(f"  Version: {pkg['version']}")
    print(f"  Entry: {pkg['entry']}")

    # Check if installed
    filename = pkg['entry'].split('/')[-1]
    local_path = AIM_DIR / filename
    if local_path.exists():
        print(f"  Status: {Colors.GREEN}Installed{Colors.END}")
    else:
        print(f"  Status: Not installed")

    print()


def cmd_config_init(args):
    """Initialize config file"""
    config_path = get_config_path()

    if config_path.exists():
        print_warning(f"Config file already exists at {config_path}")
        return

    if init_config():
        print_success(f"Created config file at {config_path}")
    else:
        print_warning("Config file already exists")


def cmd_config_get(args):
    """Get config value"""
    config = load_config()
    value = get_config_value(config, args.key)

    if value is None:
        print_error(f"Config key '{args.key}' not found")
        sys.exit(1)

    print(value)


def cmd_config_set(args):
    """Set config value"""
    config = load_config()
    config = set_config_value(config, args.key, args.value)
    save_config(config)
    print_success(f"Set {args.key} = {args.value}")


def cmd_config_list(args):
    """List all config values"""
    config = load_config()
    config_path = get_config_path()

    if config_path.exists():
        print(f"\n{Colors.BOLD}Config file:{Colors.END} {config_path}")
    else:
        print(f"\n{Colors.BOLD}Config:{Colors.END} (using defaults)")

    print()
    print(json.dumps(config, indent=2))
    print()


def cmd_synth(args):
    """Generate synthesis prompts for packages"""

    # Handle --list flag
    if args.list:
        cmd_list(args)
        return

    # Check if package specified
    if not args.package:
        print_error("Package name required (or use --interactive)")
        print_info("Usage: aim synth <package> [options]")
        print_info("   or: aim synth --interactive")
        sys.exit(1)

    # Load config
    config = load_config()

    # Handle interactive mode
    if args.interactive:
        # Get available packages
        if not AIM_DIR.exists():
            print_error("No aim/ directory found. Run 'aim init' first.")
            sys.exit(1)

        intent_files = list(AIM_DIR.glob("*.intent"))
        if not intent_files:
            print_error("No packages installed. Run 'aim fetch <package>' first.")
            sys.exit(1)

        # Extract package names from filenames
        packages = [f.stem for f in intent_files]

        prompt_data = interactive_prompt_builder(packages, config)
        if not prompt_data:
            print_info("Cancelled")
            return
    else:
        # Non-interactive mode
        package_name = args.package

        # Check if package exists
        intent_files = list(AIM_DIR.glob(f"*{package_name}*.intent"))
        if not intent_files:
            print_error(f"Package '{package_name}' not found in aim/")
            print_info("Run 'aim list' to see installed packages")
            print_info("Run 'aim fetch <package>' to install a package")
            sys.exit(1)

        # Parse tech stack
        if args.stack:
            stack = parse_stack_string(args.stack)
        else:
            stack = config.get('stack', {})

        prompt_data = {
            'package': package_name,
            'stack': stack,
            'context': ''
        }

    # Find intent files for the package
    intent_files = list(AIM_DIR.glob(f"*{prompt_data['package']}*.intent"))

    # Build prompt
    prompt = build_synthesis_prompt(
        package_name=prompt_data['package'],
        intent_files=intent_files,
        tech_stack=prompt_data['stack'],
        additional_context=prompt_data.get('context', '')
    )

    # Output prompt
    print()
    print_success("Generated synthesis prompt:")
    print()
    print(prompt)
    print()

    # Copy to clipboard by default (unless --no-copy)
    if not args.no_copy:
        if copy_to_clipboard(prompt):
            print_success("✓ Copied to clipboard!")
        else:
            print_warning("Could not copy to clipboard - please copy manually")
            print_info("(Install pbcopy/xclip/clip for automatic clipboard support)")
    else:
        print_info("Prompt displayed (not copied to clipboard)")
    print()


def main():
    parser = argparse.ArgumentParser(
        description='Sinth — the CLI for AIM. Synthesize intent into reality.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  sinth                          # Interactive menu (NEW!)
  sinth init                     # Initialize project
  sinth fetch weather            # Fetch weather package
  sinth list                     # List installed packages
  sinth validate                 # Validate intent files
  sinth info weather             # Show package info

  sinth config init              # Create config file
  sinth config set stack.frontend React
  sinth config list              # Show all config

  sinth synth weather            # Generate synthesis prompt
  sinth synth --interactive      # Interactive prompt builder
  sinth synth weather --no-copy  # Don't copy to clipboard
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # init command
    parser_init = subparsers.add_parser('init', help='Initialize AIM project')
    parser_init.set_defaults(func=cmd_init)

    # fetch command
    parser_fetch = subparsers.add_parser('fetch', help='Fetch package from registry')
    parser_fetch.add_argument('package', help='Package name')
    parser_fetch.set_defaults(func=cmd_fetch)

    # list command
    parser_list = subparsers.add_parser('list', help='List installed packages')
    parser_list.set_defaults(func=cmd_list)

    # validate command
    parser_validate = subparsers.add_parser('validate', help='Validate intent files')
    parser_validate.set_defaults(func=cmd_validate)

    # info command
    parser_info = subparsers.add_parser('info', help='Show package information')
    parser_info.add_argument('package', help='Package name')
    parser_info.set_defaults(func=cmd_info)

    # config command
    parser_config = subparsers.add_parser('config', help='Manage configuration')
    config_subparsers = parser_config.add_subparsers(dest='config_command')

    parser_config_init = config_subparsers.add_parser('init', help='Initialize config file')
    parser_config_init.set_defaults(func=cmd_config_init)

    parser_config_get = config_subparsers.add_parser('get', help='Get config value')
    parser_config_get.add_argument('key', help='Config key (e.g., stack.frontend)')
    parser_config_get.set_defaults(func=cmd_config_get)

    parser_config_set = config_subparsers.add_parser('set', help='Set config value')
    parser_config_set.add_argument('key', help='Config key (e.g., stack.frontend)')
    parser_config_set.add_argument('value', help='Config value')
    parser_config_set.set_defaults(func=cmd_config_set)

    parser_config_list = config_subparsers.add_parser('list', help='List all config')
    parser_config_list.set_defaults(func=cmd_config_list)

    # synth command
    parser_synth = subparsers.add_parser('synth', help='Generate synthesis prompts')
    parser_synth.add_argument('package', nargs='?', help='Package name')
    parser_synth.add_argument('--interactive', '-i', action='store_true',
                             help='Interactive mode')
    parser_synth.add_argument('--stack', '-s',
                             help='Tech stack (e.g., "React,Node.js,PostgreSQL")')
    parser_synth.add_argument('--no-copy', action='store_true',
                             help="Don't copy to clipboard")
    parser_synth.add_argument('--list', '-l', action='store_true',
                             help='List available packages')
    parser_synth.set_defaults(func=cmd_synth)

    # Parse arguments
    args = parser.parse_args()

    if not args.command:
        from aim_cli.menu import run_interactive_menu
        try:
            run_interactive_menu()
            sys.exit(0)
        except KeyboardInterrupt:
            print("\n")
            print_info("Goodbye!")
            sys.exit(0)

    # Execute command
    args.func(args)


if __name__ == '__main__':
    main()
