"""
PyEnvCLI Terminal User Interface - Completely fixed version.
No freezing, all operations async, single consolidated implementation.
"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, ScrollableContainer
from textual.widgets import (
    Header, Footer, Button, Input, Select, Static,
    DataTable, Label, Checkbox, OptionList
)
from textual.widgets.option_list import Option
from textual.screen import Screen, ModalScreen
from textual.binding import Binding
from textual.worker import Worker, WorkerState

from .models import VirtualEnvConfig, AIToolName
from .persistence import JSONStore
from .contracts import (
    CreateVirtualEnvContract,
    ConfigurePackagesContract,
    ConfigureDockerContract,
    PromptAIToolContract,
    ContractError
)
from .installers import PythonInstaller, PackageManager
from .flows import ValidatePythonVersionFlow


class PythonInstallDialog(ModalScreen):
    """Modal dialog for installing missing Python versions."""

    def __init__(self, python_version: str):
        super().__init__()
        self.python_version = python_version
        self.available_managers = PythonInstaller.detect_available_managers()
        self.current_command = None

    def compose(self) -> ComposeResult:
        yield Container(
            Static(f"⚠️  [bold yellow]Python {self.python_version} Not Found[/bold yellow]", id="dialog_title"),
            Static(
                f"\nPython {self.python_version} is not installed.\n"
                "Select a package manager:",
                id="dialog_message"
            ),
            OptionList(
                *[Option(str(pm.value).title(), id=pm.value) for pm in self.available_managers],
                id="manager_list"
            ),
            Static("", id="install_command"),
            Horizontal(
                Button("Copy Command", variant="primary", id="btn_copy"),
                Button("Cancel", variant="default", id="btn_cancel"),
                id="dialog_buttons"
            ),
            id="install_dialog"
        )

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        """Show installation command."""
        manager = PackageManager(event.option.id)
        description, cmd_parts = PythonInstaller.get_install_command(manager, self.python_version)
        command_widget = self.query_one("#install_command", Static)

        if manager == PackageManager.MANUAL:
            url = PythonInstaller.get_installation_url(self.python_version)
            self.current_command = url
            command_widget.update(f"\n[yellow]Visit:[/yellow]\n{url}\n")
        else:
            cmd_string = " ".join(cmd_parts)
            self.current_command = cmd_string
            command_widget.update(
                f"\n[yellow]Command:[/yellow]\n"
                f"[cyan]{cmd_string}[/cyan]\n\n"
                f"[dim]Run in terminal, then restart[/dim]"
            )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks."""
        if event.button.id == "btn_cancel":
            self.dismiss(None)
        elif event.button.id == "btn_copy":
            if self.current_command:
                try:
                    # Try to copy to clipboard using pbcopy on macOS
                    import subprocess
                    subprocess.run(['pbcopy'], input=self.current_command.encode(), check=True)
                    command_widget = self.query_one("#install_command", Static)
                    command_widget.update(
                        f"\n[yellow]Command:[/yellow]\n"
                        f"[cyan]{self.current_command}[/cyan]\n\n"
                        f"[green]✓ Copied to clipboard![/green]"
                    )
                    self.app.bell()
                except Exception:
                    # Fallback: just show the command
                    command_widget = self.query_one("#install_command", Static)
                    command_widget.update(
                        f"\n[yellow]Command:[/yellow]\n"
                        f"[cyan]{self.current_command}[/cyan]\n\n"
                        f"[green]✓ Ready to copy (manually)![/green]"
                    )
                    self.app.bell()
            else:
                command_widget = self.query_one("#install_command", Static)
                command_widget.update("[red]Please select a package manager first[/red]")


class PackageSearchDialog(ModalScreen):
    """Modal dialog for searching packages."""

    COMMON_PACKAGES = [
        # Web Frameworks
        ("flask", "Lightweight web framework"),
        ("django", "Full-featured web framework"),
        ("fastapi", "Modern async web framework"),
        ("streamlit", "Web apps for data science"),
        ("bottle", "Micro web framework"),
        ("tornado", "Async web framework"),
        ("aiohttp", "Async HTTP client/server"),
        ("sanic", "Async web framework"),

        # HTTP & API
        ("requests", "HTTP library"),
        ("httpx", "Next-gen HTTP client"),
        ("urllib3", "HTTP client"),
        ("beautifulsoup4", "HTML/XML parser"),
        ("scrapy", "Web scraping framework"),
        ("selenium", "Web browser automation"),

        # Data Science & ML
        ("numpy", "Numerical computing"),
        ("pandas", "Data analysis"),
        ("scipy", "Scientific computing"),
        ("scikit-learn", "Machine learning"),
        ("tensorflow", "Deep learning framework"),
        ("pytorch", "Deep learning framework"),
        ("keras", "Neural networks API"),
        ("xgboost", "Gradient boosting"),
        ("lightgbm", "Gradient boosting"),

        # Visualization
        ("matplotlib", "Plotting library"),
        ("seaborn", "Statistical visualization"),
        ("plotly", "Interactive plots"),
        ("bokeh", "Interactive visualization"),
        ("altair", "Declarative visualization"),

        # Testing
        ("pytest", "Testing framework"),
        ("unittest", "Unit testing framework"),
        ("nose2", "Testing framework"),
        ("coverage", "Code coverage tool"),
        ("mock", "Mocking library"),
        ("tox", "Testing automation"),
        ("hypothesis", "Property-based testing"),

        # Database
        ("sqlalchemy", "SQL toolkit and ORM"),
        ("psycopg2", "PostgreSQL adapter"),
        ("pymongo", "MongoDB driver"),
        ("redis", "Redis client"),
        ("mysql-connector-python", "MySQL driver"),
        ("alembic", "Database migrations"),

        # Code Quality
        ("black", "Code formatter"),
        ("mypy", "Static type checker"),
        ("pylint", "Code linter"),
        ("flake8", "Style guide enforcer"),
        ("isort", "Import sorter"),
        ("autopep8", "Auto formatter"),
        ("bandit", "Security linter"),
        ("ruff", "Fast Python linter"),

        # Utilities
        ("click", "CLI creation kit"),
        ("rich", "Terminal formatting"),
        ("pydantic", "Data validation"),
        ("python-dotenv", "Environment variables"),
        ("loguru", "Logging library"),
        ("tqdm", "Progress bars"),
        ("pillow", "Image processing"),
        ("openpyxl", "Excel files"),
        ("pyyaml", "YAML parser"),
        ("jinja2", "Template engine"),

        # Async & Concurrency
        ("asyncio", "Async I/O"),
        ("celery", "Distributed task queue"),
        ("gevent", "Coroutine networking"),

        # DevOps & Cloud
        ("boto3", "AWS SDK"),
        ("docker", "Docker SDK"),
        ("ansible", "Automation platform"),
        ("paramiko", "SSH library"),

        # API Development
        ("graphene", "GraphQL framework"),
        ("marshmallow", "Serialization"),
        ("pyjwt", "JSON Web Tokens"),
        ("python-jose", "JWT implementation"),
    ]

    def __init__(self):
        super().__init__()
        self.selected_packages: List[dict] = []

    def compose(self) -> ComposeResult:
        yield Container(
            Static("📦 [bold cyan]Package Search[/bold cyan]", id="search_title"),
            Input(placeholder="Type to search...", id="search_input"),
            OptionList(
                *[Option(f"{name} - {desc}", id=name) for name, desc in self.COMMON_PACKAGES],
                id="package_list"
            ),
            Label("Version (optional):"),
            Input(placeholder="e.g., ==2.31.0, >=1.0.0", id="version_input"),
            ScrollableContainer(
                Static("", id="selected_display"),
                id="selected_container"
            ),
            Horizontal(
                Button("Add", variant="success", id="btn_add"),
                Button("Done", variant="primary", id="btn_done"),
                Button("Cancel", variant="default", id="btn_cancel"),
                id="search_buttons"
            ),
            id="search_dialog"
        )

    def on_input_changed(self, event: Input.Changed) -> None:
        """Filter packages."""
        if event.input.id == "search_input":
            search_term = event.value.lower()
            filtered = [
                (name, desc) for name, desc in self.COMMON_PACKAGES
                if search_term in name.lower() or search_term in desc.lower()
            ] if search_term else self.COMMON_PACKAGES

            package_list = self.query_one("#package_list", OptionList)
            package_list.clear_options()
            for name, desc in filtered:
                package_list.add_option(Option(f"{name} - {desc}", id=name))

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        """Auto-fill search."""
        self.query_one("#search_input", Input).value = event.option.id

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle buttons."""
        if event.button.id == "btn_cancel":
            self.dismiss([])
        elif event.button.id == "btn_done":
            self.dismiss(self.selected_packages)
        elif event.button.id == "btn_add":
            search_input = self.query_one("#search_input", Input)
            version_input = self.query_one("#version_input", Input)
            display = self.query_one("#selected_display", Static)

            if not search_input.value:
                display.update("[red]Enter package name[/red]")
                return

            self.selected_packages.append({
                "name": search_input.value,
                "version": version_input.value if version_input.value else None
            })

            text = "\n[bold]Selected:[/bold]\n"
            for pkg in self.selected_packages:
                text += f"  • {pkg['name']} ({pkg['version'] or 'latest'})\n"
            display.update(text)

            search_input.value = ""
            version_input.value = ""


class WelcomeScreen(Screen):
    """Main dashboard."""

    BINDINGS = [
        ("n", "new_env", "New"),
        ("r", "refresh", "Refresh"),
        ("q", "quit", "Quit"),
    ]

    def __init__(self):
        super().__init__()
        self.store = JSONStore()

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("🐍 [bold cyan]PyEnvCLI[/bold cyan]", id="title"),
            Static("Python Virtual Environment Manager", id="subtitle"),
            DataTable(id="env_table"),
            Horizontal(
                Button("New", variant="primary", id="btn_new"),
                Button("Refresh", variant="default", id="btn_refresh"),
                Button("Quit", variant="error", id="btn_quit"),
                id="buttons"
            ),
            id="main"
        )
        yield Footer()

    def on_mount(self) -> None:
        """Setup table."""
        table = self.query_one("#env_table", DataTable)
        table.add_columns("ID", "Name", "Python", "Docker", "Created")
        table.cursor_type = "row"
        self.load_environments()

    def load_environments(self) -> None:
        """Load envs, filtering out non-existent ones."""
        from pathlib import Path
        table = self.query_one("#env_table", DataTable)
        table.clear()
        try:
            configs_to_remove = []
            for cfg in sorted(self.store.list_configs(), key=lambda c: c.createdAt, reverse=True):
                # Check if environment directory exists
                env_path = Path(cfg.projectPath) / cfg.envName
                if env_path.exists() and env_path.is_dir():
                    table.add_row(
                        str(cfg.id)[:8],
                        cfg.envName,
                        cfg.pythonVersion,
                        "✓" if cfg.includeDockerfile else "✗",
                        cfg.createdAt.strftime("%Y-%m-%d %H:%M")
                    )
                else:
                    # Mark stale config for removal
                    configs_to_remove.append(cfg.id)

            # Clean up stale configs
            for config_id in configs_to_remove:
                self.store.delete_config(config_id)
        except:
            pass

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle buttons."""
        if event.button.id == "btn_new":
            self.app.push_screen(CreateEnvironmentScreen())
        elif event.button.id == "btn_refresh":
            self.load_environments()
        elif event.button.id == "btn_quit":
            self.app.exit()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle selection."""
        if event.row_key:
            try:
                row_data = list(event.data_table.get_row(event.row_key))
                self.app.push_screen(EnvironmentDetailScreen(row_data[0]))
            except:
                pass

    def action_new_env(self) -> None:
        self.app.push_screen(CreateEnvironmentScreen())

    def action_refresh(self) -> None:
        self.load_environments()

    def action_quit(self) -> None:
        self.app.exit()


class CreateEnvironmentScreen(Screen):
    """Create new environment."""

    BINDINGS = [("escape", "back", "Back")]

    def __init__(self):
        super().__init__()
        self.store = JSONStore()
        self.check_worker_running = False
        self.create_worker_running = False

    def compose(self) -> ComposeResult:
        yield Header()
        yield ScrollableContainer(
            Static("🆕 [bold cyan]Create Environment[/bold cyan]", id="title"),
            Label("Name:"),
            Input(placeholder="myenv", id="input_name"),
            Label("Python Version:"),
            Select(
                [("Python 3.8", "3.8"), ("Python 3.9", "3.9"), ("Python 3.10", "3.10"),
                 ("Python 3.11", "3.11"), ("Python 3.12", "3.12"), ("Python 3.13", "3.13")],
                value="3.11",
                id="select_python"
            ),
            Button("Check Version", id="btn_check"),
            Static("", id="check_status"),
            Label("Path:"),
            Input(value=".", id="input_path"),
            Checkbox("Generate Dockerfile", id="check_docker"),
            Checkbox("Generate requirements.txt", value=True, id="check_req"),
            Static("", id="create_status"),
            Horizontal(
                Button("Create", variant="primary", id="btn_create"),
                Button("Cancel", id="btn_cancel"),
                id="buttons"
            ),
            id="container"
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle buttons."""
        if event.button.id == "btn_check":
            if not self.check_worker_running:
                self.check_python_async()
        elif event.button.id == "btn_create":
            if not self.create_worker_running:
                self.create_environment_async()
        elif event.button.id == "btn_cancel":
            self.app.pop_screen()

    def check_python_async(self) -> None:
        """Check Python version async."""
        python_select = self.query_one("#select_python", Select)
        status = self.query_one("#check_status", Static)
        status.update("[yellow]⏳ Checking...[/yellow]")

        self.check_worker_running = True
        self.run_worker(
            self._check_python(str(python_select.value)),
            name="check_python",
            group="python_check"
        )

    async def _check_python(self, version: str) -> tuple:
        """Check worker."""
        return ValidatePythonVersionFlow.execute(version)

    def create_environment_async(self) -> None:
        """Create environment async."""
        name_input = self.query_one("#input_name", Input)
        python_select = self.query_one("#select_python", Select)
        path_input = self.query_one("#input_path", Input)
        docker_check = self.query_one("#check_docker", Checkbox)
        req_check = self.query_one("#check_req", Checkbox)
        status = self.query_one("#create_status", Static)

        if not name_input.value:
            status.update("[red]❌ Name required[/red]")
            return

        status.update("[yellow]⏳ Creating...[/yellow]")
        self.create_worker_running = True

        self.run_worker(
            self._create_env(
                name_input.value,
                str(python_select.value),
                path_input.value,
                docker_check.value,
                req_check.value
            ),
            name="create_env",
            group="env_creation"
        )

    async def _create_env(self, name, python_ver, path, docker, req) -> dict:
        """Create worker."""
        success, python_path, error = ValidatePythonVersionFlow.execute(python_ver)
        if not success:
            raise ContractError(error)

        contract = CreateVirtualEnvContract(self.store)
        return contract.execute(
            env_name=name,
            python_version=python_ver,
            project_path=path,
            include_dockerfile=docker,
            include_requirements=req,
            ai_tool_preference=None
        )

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        """Handle worker completion."""
        if event.worker.group == "python_check":
            self.check_worker_running = False
            status = self.query_one("#check_status", Static)

            if event.state == WorkerState.SUCCESS:
                success, python_path, error = event.worker.result
                if success:
                    status.update(f"[green]✓ Found![/green]\n{python_path}")
                else:
                    status.update(f"[red]✗ Not found[/red]")
                    python_select = self.query_one("#select_python", Select)
                    self.app.push_screen(PythonInstallDialog(str(python_select.value)))
            elif event.state == WorkerState.ERROR:
                status.update(f"[red]Error: {event.worker.error}[/red]")

        elif event.worker.group == "env_creation":
            self.create_worker_running = False
            status = self.query_one("#create_status", Static)

            if event.state == WorkerState.SUCCESS:
                result = event.worker.result
                status.update(f"[green]✓ Created![/green]\n{result['activation_command']}")
                # Refresh the parent screen's environment list before popping
                if hasattr(self.app.screen_stack[0], 'load_environments'):
                    self.app.screen_stack[0].load_environments()
                # Return to main screen without timer to avoid freezing
                self.app.pop_screen()
            elif event.state == WorkerState.ERROR:
                status.update(f"[red]Error: {event.worker.error}[/red]")

    def action_back(self) -> None:
        self.app.pop_screen()


class EnvironmentDetailScreen(Screen):
    """Environment details."""

    BINDINGS = [
        ("escape", "back", "Back"),
        ("p", "packages", "Packages"),
        ("d", "delete", "Delete"),
    ]

    def __init__(self, config_id: str):
        super().__init__()
        self.config_id = config_id
        self.store = JSONStore()
        self.config = None
        self.delete_worker_running = False

    def compose(self) -> ComposeResult:
        yield Header()
        yield ScrollableContainer(
            Static("", id="title"),
            Static("", id="info"),
            Static("", id="packages"),
            Static("", id="delete_status"),
            Horizontal(
                Button("📦 Packages", variant="primary", id="btn_packages"),
                Button("🗑️  Delete", variant="error", id="btn_delete"),
                Button("← Back", id="btn_back"),
                id="buttons"
            ),
            id="container"
        )
        yield Footer()

    def on_mount(self) -> None:
        """Load details."""
        try:
            for cfg in self.store.list_configs():
                if str(cfg.id).startswith(self.config_id):
                    self.config = cfg
                    break

            if not self.config:
                self.query_one("#title", Static).update("[red]Not found[/red]")
                return

            self.query_one("#title", Static).update(f"📁 [bold cyan]{self.config.envName}[/bold cyan]")
            self.query_one("#info", Static).update(
                f"\n[cyan]ID:[/cyan] {str(self.config.id)[:8]}\n"
                f"[cyan]Python:[/cyan] {self.config.pythonVersion}\n"
                f"[cyan]Path:[/cyan] {self.config.projectPath}\n"
            )

            packages = self.store.get_packages_for_config(self.config.id)
            if packages:
                text = "\n[bold]Packages:[/bold]\n"
                for pkg in packages:
                    text += f"  • {pkg.packageName} ({pkg.versionSpec or 'latest'})\n"
                self.query_one("#packages", Static).update(text)
        except Exception as e:
            self.query_one("#title", Static).update(f"[red]Error: {e}[/red]")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle buttons."""
        if event.button.id == "btn_packages" and self.config:
            self.app.push_screen(PackageManagementScreen(str(self.config.id)))
        elif event.button.id == "btn_delete" and self.config:
            if not self.delete_worker_running:
                self.delete_environment_async()
        elif event.button.id == "btn_back":
            self.app.pop_screen()

    def delete_environment_async(self) -> None:
        """Delete environment async."""
        status = self.query_one("#delete_status", Static)
        status.update("[yellow]⏳ Deleting environment...[/yellow]")
        self.delete_worker_running = True

        self.run_worker(
            self._delete_environment(),
            name="delete_env",
            group="env_deletion"
        )

    async def _delete_environment(self) -> dict:
        """Delete worker."""
        import shutil
        from pathlib import Path

        # Delete the virtual environment directory
        env_path = Path(self.config.projectPath) / self.config.envName
        if env_path.exists():
            shutil.rmtree(env_path)

        # Delete from storage
        self.store.delete_config(self.config.id)

        return {"success": True, "env_name": self.config.envName}

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        """Handle worker completion."""
        if event.worker.group == "env_deletion":
            self.delete_worker_running = False
            status = self.query_one("#delete_status", Static)

            if event.state == WorkerState.SUCCESS:
                result = event.worker.result
                status.update(f"[green]✓ Deleted {result['env_name']}![/green]")
                # Refresh the parent screen's environment list
                if hasattr(self.app.screen_stack[0], 'load_environments'):
                    self.app.screen_stack[0].load_environments()
                # Return to main screen
                self.app.pop_screen()
            elif event.state == WorkerState.ERROR:
                status.update(f"[red]Error: {event.worker.error}[/red]")

    def action_back(self) -> None:
        self.app.pop_screen()

    def action_packages(self) -> None:
        if self.config:
            self.app.push_screen(PackageManagementScreen(str(self.config.id)))

    def action_delete(self) -> None:
        if self.config and not self.delete_worker_running:
            self.delete_environment_async()


class PackageManagementScreen(Screen):
    """Manage packages."""

    BINDINGS = [
        ("escape", "back", "Back"),
        ("s", "search", "Search"),
    ]

    def __init__(self, config_id: str):
        super().__init__()
        self.config_id = config_id
        self.store = JSONStore()
        self.pending = []
        self.save_worker_running = False

    def compose(self) -> ComposeResult:
        yield Header()
        yield ScrollableContainer(
            Static("📦 [bold cyan]Packages[/bold cyan]", id="title"),
            Static("", id="current"),
            Button("Search Packages", variant="primary", id="btn_search"),
            Label("Or add manually:"),
            Input(placeholder="package name", id="input_name"),
            Input(placeholder="version (optional)", id="input_version"),
            Button("Add", variant="success", id="btn_add"),
            Static("", id="pending"),
            Static("", id="status"),
            Horizontal(
                Button("Save All", variant="primary", id="btn_save"),
                Button("← Back", id="btn_back"),
                id="buttons"
            ),
            id="container"
        )
        yield Footer()

    def on_mount(self) -> None:
        """Load packages."""
        self.load_current()

    def load_current(self) -> None:
        """Load current packages."""
        try:
            packages = self.store.get_packages_for_config(UUID(self.config_id))
            if packages:
                text = "\n[bold]Current:[/bold]\n"
                for pkg in packages:
                    text += f"  • {pkg.packageName} ({pkg.versionSpec or 'latest'})\n"
                self.query_one("#current", Static).update(text)
        except:
            pass

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle buttons."""
        if event.button.id == "btn_search":
            self.app.push_screen(PackageSearchDialog(), self.handle_search)
        elif event.button.id == "btn_add":
            self.add_manual()
        elif event.button.id == "btn_save":
            if not self.save_worker_running:
                self.save_async()
        elif event.button.id == "btn_back":
            self.app.pop_screen()

    def handle_search(self, packages: List[dict]) -> None:
        """Handle search results."""
        if packages:
            self.pending.extend(packages)
            self.update_pending()

    def add_manual(self) -> None:
        """Add package manually."""
        name_input = self.query_one("#input_name", Input)
        version_input = self.query_one("#input_version", Input)

        if name_input.value:
            self.pending.append({
                "name": name_input.value,
                "version": version_input.value if version_input.value else None
            })
            name_input.value = ""
            version_input.value = ""
            self.update_pending()

    def update_pending(self) -> None:
        """Update pending display."""
        if self.pending:
            text = "\n[bold]To add:[/bold]\n"
            for pkg in self.pending:
                text += f"  • {pkg['name']} ({pkg['version'] or 'latest'})\n"
            self.query_one("#pending", Static).update(text)

    def save_async(self) -> None:
        """Save packages async."""
        if not self.pending:
            self.query_one("#status", Static).update("[yellow]Nothing to save[/yellow]")
            return

        self.query_one("#status", Static).update("[yellow]⏳ Saving...[/yellow]")
        self.save_worker_running = True

        self.run_worker(
            self._save_packages(),
            name="save_packages",
            group="package_save"
        )

    async def _save_packages(self) -> dict:
        """Save worker."""
        contract = ConfigurePackagesContract(self.store)
        return contract.execute(self.config_id, self.pending)

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        """Handle worker completion."""
        if event.worker.group == "package_save":
            self.save_worker_running = False
            status = self.query_one("#status", Static)

            if event.state == WorkerState.SUCCESS:
                result = event.worker.result
                status.update(f"[green]✓ Saved {result['packages_count']} packages[/green]")
                self.pending = []
                self.query_one("#pending", Static).update("")
                self.load_current()
            elif event.state == WorkerState.ERROR:
                status.update(f"[red]Error: {event.worker.error}[/red]")

    def action_back(self) -> None:
        self.app.pop_screen()

    def action_search(self) -> None:
        self.app.push_screen(PackageSearchDialog(), self.handle_search)


class PyEnvTUI(App):
    """PyEnvCLI TUI."""

    CSS = """
    Screen { background: $surface; }
    #title { text-align: center; padding: 1; background: $primary; }
    #subtitle { text-align: center; padding: 0 0 1 0; color: $text-muted; }
    #main, #container { padding: 1; height: 100%; }
    #env_table { height: 1fr; margin: 1 0; }
    #buttons { height: auto; margin: 1 0; align: center middle; }
    Button { margin: 0 1; }
    Input, Select { margin: 0 0 1 0; }
    Label { margin: 1 0 0 0; text-style: bold; }
    #install_dialog, #search_dialog { width: 70; height: auto; padding: 2; background: $surface; border: thick $primary; }
    OptionList { height: 15; margin: 1 0; }
    #selected_container { height: 8; margin: 1 0; border: solid $primary; }
    #selected_display { height: auto; }
    """

    TITLE = "PyEnvCLI"

    def on_mount(self) -> None:
        self.push_screen(WelcomeScreen())


def run_tui():
    """Entry point."""
    app = PyEnvTUI()
    app.run()


if __name__ == "__main__":
    run_tui()
