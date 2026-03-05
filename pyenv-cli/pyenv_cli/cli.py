"""
VIEW layer - Interactive CLI interface using Click and Rich.
Maps PERSONA views to CLI commands and prompts.
"""

import os
import sys
from pathlib import Path
from typing import List, Optional

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich import print as rprint

from .models import AIToolName
from .persistence import JSONStore
from .contracts import (
    CreateVirtualEnvContract,
    ConfigurePackagesContract,
    ConfigureDockerContract,
    PromptAIToolContract,
    ContractError
)

console = Console()


def get_store() -> JSONStore:
    """Get JSONStore instance for current directory."""
    return JSONStore()


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """
    PyEnvCLI - Python Virtual Environment Generator with AI Integration

    A CLI tool for creating and managing Python virtual environments with
    support for AI-assisted development workflows.
    """
    pass


@cli.command(name="create")
@click.option("--name", "-n", help="Environment name")
@click.option("--python", "-p", help="Python version (e.g., 3.11)")
@click.option("--path", "-d", help="Project directory path", default=".")
@click.option("--docker/--no-docker", default=None, help="Generate Dockerfile")
@click.option("--requirements/--no-requirements", default=True, help="Generate requirements.txt")
@click.option("--ai-tool", "-a", type=click.Choice([t.value for t in AIToolName]), help="AI tool preference")
def create_env(
    name: Optional[str],
    python: Optional[str],
    path: str,
    docker: Optional[bool],
    requirements: bool,
    ai_tool: Optional[str]
):
    """
    VIEW: EnvironmentSetup
    Interactive wizard for creating a Python virtual environment.

    ACTIONS:
        - Create Environment -> Contract.CreateVirtualEnv
    """
    console.print("\n[bold cyan]🐍 PyEnvCLI - Virtual Environment Setup[/bold cyan]\n")

    # Interactive prompts if options not provided
    if not name:
        name = Prompt.ask(
            "[yellow]Environment name[/yellow]",
            default="venv"
        )

    if not python:
        python = Prompt.ask(
            "[yellow]Python version[/yellow]",
            choices=["3.8", "3.9", "3.10", "3.11", "3.12", "3.13"],
            default="3.11"
        )

    # Resolve absolute path
    project_path = str(Path(path).resolve())

    if docker is None:
        docker = Confirm.ask(
            "[yellow]Generate Dockerfile?[/yellow]",
            default=False
        )

    # Execute contract
    store = get_store()
    contract = CreateVirtualEnvContract(store)

    try:
        with console.status("[bold green]Creating virtual environment..."):
            result = contract.execute(
                env_name=name,
                python_version=python,
                project_path=project_path,
                include_dockerfile=docker,
                include_requirements=requirements,
                ai_tool_preference=ai_tool
            )

        # Display success
        console.print("\n[bold green]✓ Virtual environment created successfully![/bold green]\n")

        # Show details
        details_table = Table(show_header=False, box=None)
        details_table.add_row("[cyan]Environment:[/cyan]", result["env_name"])
        details_table.add_row("[cyan]Location:[/cyan]", result["env_path"])
        details_table.add_row("[cyan]Config ID:[/cyan]", result["config_id"])

        console.print(details_table)

        # Show activation instructions
        console.print(
            Panel(
                f"[yellow]{result['activation_command']}[/yellow]",
                title="[bold]Activation Command[/bold]",
                border_style="green"
            )
        )

        # Show generated files
        if result["files_generated"]:
            console.print("\n[cyan]Generated files:[/cyan]")
            for file_path in result["files_generated"]:
                console.print(f"  • {file_path}")

        console.print(f"\n[dim]Tip: Use 'pyenv-cli packages {result['config_id'][:8]}' to manage dependencies[/dim]\n")

    except ContractError as e:
        console.print(f"\n[bold red]✗ Error:[/bold red] {str(e)}\n", style="red")
        sys.exit(1)


@cli.command(name="packages")
@click.argument("config_id")
@click.option("--add", "-a", multiple=True, help="Add package (format: name or name==version)")
def manage_packages(config_id: str, add: tuple):
    """
    VIEW: PackageManager
    Manage Python package dependencies.

    ACTIONS:
        - Add Package -> Contract.ConfigurePackages
    """
    console.print(f"\n[bold cyan]📦 Package Management[/bold cyan]\n")

    store = get_store()

    # Find config by partial ID match
    configs = store.list_configs()
    matching_config = None
    for cfg in configs:
        if str(cfg.id).startswith(config_id):
            matching_config = cfg
            break

    if not matching_config:
        console.print(f"[bold red]✗ Configuration not found:[/bold red] {config_id}\n", style="red")
        sys.exit(1)

    # Interactive package addition
    packages_to_add = []

    if add:
        # Parse packages from command line
        for pkg_spec in add:
            if "==" in pkg_spec:
                name, version = pkg_spec.split("==", 1)
                packages_to_add.append({"name": name, "version": f"=={version}"})
            else:
                packages_to_add.append({"name": pkg_spec, "version": None})
    else:
        # Interactive mode
        console.print("[yellow]Add packages (enter blank line to finish):[/yellow]\n")
        while True:
            pkg_name = Prompt.ask("  Package name", default="")
            if not pkg_name:
                break

            pkg_version = Prompt.ask("  Version (optional)", default="")
            packages_to_add.append({
                "name": pkg_name,
                "version": pkg_version if pkg_version else None
            })

    if not packages_to_add:
        console.print("[yellow]No packages to add.[/yellow]\n")
        return

    # Execute contract
    contract = ConfigurePackagesContract(store)

    try:
        result = contract.execute(
            env_config_id=str(matching_config.id),
            packages=packages_to_add
        )

        console.print(f"\n[bold green]✓ Added {result['packages_count']} package(s)[/bold green]")
        console.print(f"[cyan]Requirements file:[/cyan] {result['requirements_path']}\n")

    except ContractError as e:
        console.print(f"\n[bold red]✗ Error:[/bold red] {str(e)}\n", style="red")
        sys.exit(1)


@cli.command(name="docker")
@click.argument("config_id")
@click.option("--port", "-p", multiple=True, type=int, help="Expose port")
@click.option("--command", "-c", multiple=True, help="Additional Docker command")
def setup_docker(config_id: str, port: tuple, command: tuple):
    """
    Generate Dockerfile for environment.

    ACTIONS:
        - Setup Docker -> Contract.ConfigureDocker
    """
    console.print(f"\n[bold cyan]🐳 Docker Configuration[/bold cyan]\n")

    store = get_store()

    # Find config by partial ID match
    configs = store.list_configs()
    matching_config = None
    for cfg in configs:
        if str(cfg.id).startswith(config_id):
            matching_config = cfg
            break

    if not matching_config:
        console.print(f"[bold red]✗ Configuration not found:[/bold red] {config_id}\n", style="red")
        sys.exit(1)

    # Execute contract
    contract = ConfigureDockerContract(store)

    try:
        result = contract.execute(
            env_config_id=str(matching_config.id),
            exposed_ports=list(port) if port else None,
            additional_commands=list(command) if command else None
        )

        console.print(f"[bold green]✓ Dockerfile generated[/bold green]")
        console.print(f"[cyan]Location:[/cyan] {result['dockerfile_path']}\n")

        # Show build instructions
        console.print(Panel(
            f"[yellow]{result['build_command']}[/yellow]\n"
            f"[yellow]{result['run_command']}[/yellow]",
            title="[bold]Docker Commands[/bold]",
            border_style="green"
        ))
        console.print()

    except ContractError as e:
        console.print(f"\n[bold red]✗ Error:[/bold red] {str(e)}\n", style="red")
        sys.exit(1)


@cli.command(name="ai")
@click.argument("config_id")
@click.option("--tool", "-t", type=click.Choice([t.value for t in AIToolName if t != AIToolName.NONE]), help="AI tool to launch")
@click.option("--prompt", "-p", help="Custom prompt for AI tool")
def launch_ai_tool(config_id: str, tool: Optional[str], prompt: Optional[str]):
    """
    VIEW: AIToolLauncher
    Launch AI CLI tool with environment context.

    ACTIONS:
        - Launch AI Tool -> Contract.PromptAITool
    """
    console.print(f"\n[bold cyan]🤖 AI Assistant Launcher[/bold cyan]\n")

    store = get_store()

    # Find config by partial ID match
    configs = store.list_configs()
    matching_config = None
    for cfg in configs:
        if str(cfg.id).startswith(config_id):
            matching_config = cfg
            break

    if not matching_config:
        console.print(f"[bold red]✗ Configuration not found:[/bold red] {config_id}\n", style="red")
        sys.exit(1)

    # Interactive tool selection if not provided
    if not tool:
        console.print("[yellow]Available AI Tools:[/yellow]\n")
        tools = [t for t in AIToolName if t != AIToolName.NONE]
        for i, t in enumerate(tools, 1):
            console.print(f"  {i}. {t.value}")

        choice = Prompt.ask(
            "\n[yellow]Select AI tool[/yellow]",
            choices=[str(i) for i in range(1, len(tools) + 1)]
        )
        tool = tools[int(choice) - 1].value

    if not prompt:
        prompt = Prompt.ask(
            "[yellow]Custom prompt (optional)[/yellow]",
            default="Help me set up this Python environment"
        )

    # Execute contract
    contract = PromptAIToolContract(store)

    try:
        result = contract.execute(
            env_config_id=str(matching_config.id),
            ai_tool_name=tool,
            custom_prompt=prompt
        )

        if result["success"]:
            console.print(result["message"])
        else:
            console.print(f"[bold red]✗ Error:[/bold red] {result['message']}\n", style="red")
            sys.exit(1)

    except ContractError as e:
        console.print(f"\n[bold red]✗ Error:[/bold red] {str(e)}\n", style="red")
        sys.exit(1)


@cli.command(name="list")
def list_environments():
    """
    List all configured virtual environments.
    """
    console.print("\n[bold cyan]📋 Virtual Environments[/bold cyan]\n")

    store = get_store()
    configs = store.list_configs()

    if not configs:
        console.print("[yellow]No environments configured yet.[/yellow]\n")
        console.print("[dim]Tip: Use 'pyenv-cli create' to create your first environment[/dim]\n")
        return

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("ID", style="dim")
    table.add_column("Name", style="green")
    table.add_column("Python", style="yellow")
    table.add_column("Docker", justify="center")
    table.add_column("Created", style="dim")

    for cfg in sorted(configs, key=lambda c: c.createdAt, reverse=True):
        table.add_row(
            str(cfg.id)[:8],
            cfg.envName,
            cfg.pythonVersion,
            "✓" if cfg.includeDockerfile else "✗",
            cfg.createdAt.strftime("%Y-%m-%d %H:%M")
        )

    console.print(table)
    console.print()


if __name__ == "__main__":
    cli()
