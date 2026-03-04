"""
FLOW services - Internal business logic orchestration.
Implements step-by-step workflows as defined in AIM specification.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from uuid import UUID

from .models import (
    VirtualEnvConfig,
    PackageRequirement,
    DockerConfiguration,
    AIToolSession,
    AIToolName,
    AISessionStatus
)
from .persistence import JSONStore


class FlowError(Exception):
    """Base exception for flow execution errors."""
    pass


class ValidatePythonVersionFlow:
    """
    FLOW: ValidatePythonVersion
    Validates that the requested Python version is available on the system.
    """

    @staticmethod
    def execute(python_version: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Validate Python version availability.

        Returns:
            (success: bool, python_path: str, error_message: str)
        """
        # Extract major.minor version
        version_parts = python_version.split('.')
        major_minor = f"{version_parts[0]}.{version_parts[1]}"

        # Try different Python executable names
        python_commands = [
            f"python{major_minor}",
            f"python{version_parts[0]}",
            "python3",
            "python"
        ]

        for cmd in python_commands:
            try:
                result = subprocess.run(
                    [cmd, "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    # Check if version matches
                    version_output = result.stdout.strip()
                    if major_minor in version_output:
                        # Get full path
                        path_result = subprocess.run(
                            ["which", cmd],
                            capture_output=True,
                            text=True
                        )
                        python_path = path_result.stdout.strip()
                        return (True, python_path or cmd, None)
            except (subprocess.TimeoutExpired, FileNotFoundError):
                continue

        error_msg = (
            f"Python {python_version} not found on system. "
            f"Please install it using your package manager or from python.org"
        )
        return (False, None, error_msg)


class GenerateRequirementsListFlow:
    """
    FLOW: GenerateRequirementsList
    Creates requirements.txt from user-specified packages.
    """

    def __init__(self, store: JSONStore):
        self.store = store

    def execute(self, config_id: UUID, project_path: str) -> str:
        """
        Generate requirements.txt file.

        Returns:
            Path to generated requirements.txt
        """
        packages = self.store.get_packages_for_config(config_id)

        # Build requirements.txt content
        lines = []
        for pkg in packages:
            if pkg.versionSpec:
                lines.append(f"{pkg.packageName}{pkg.versionSpec}")
            else:
                lines.append(pkg.packageName)

        # Write to project path
        requirements_path = Path(project_path) / "requirements.txt"
        with open(requirements_path, 'w') as f:
            f.write('\n'.join(lines) + '\n')

        return str(requirements_path)


class GenerateDockerfileFlow:
    """
    FLOW: GenerateDockerfile
    Creates an optimized Dockerfile for the Python environment.
    """

    def __init__(self, store: JSONStore):
        self.store = store

    def execute(
        self,
        config_id: UUID,
        python_version: str,
        project_path: str,
        exposed_ports: Optional[List[int]] = None,
        additional_commands: Optional[List[str]] = None
    ) -> str:
        """
        Generate Dockerfile.

        Returns:
            Path to generated Dockerfile
        """
        # Extract major.minor version for base image
        version_parts = python_version.split('.')
        major_minor = f"{version_parts[0]}.{version_parts[1]}"
        base_image = f"python:{major_minor}-slim"

        # Build Dockerfile content
        dockerfile_lines = [
            f"FROM {base_image}",
            "",
            "# Set working directory",
            "WORKDIR /app",
            "",
            "# Copy requirements first for layer caching",
            "COPY requirements.txt .",
            "",
            "# Install dependencies",
            "RUN pip install --no-cache-dir -r requirements.txt",
            "",
            "# Copy application code",
            "COPY . .",
            ""
        ]

        # Add exposed ports
        if exposed_ports:
            for port in exposed_ports:
                dockerfile_lines.append(f"EXPOSE {port}")
            dockerfile_lines.append("")

        # Add additional commands
        if additional_commands:
            dockerfile_lines.append("# Additional configuration")
            dockerfile_lines.extend(additional_commands)
            dockerfile_lines.append("")

        # Add default command
        dockerfile_lines.extend([
            "# Default command",
            'CMD ["python", "-m", "app"]'
        ])

        dockerfile_content = '\n'.join(dockerfile_lines)

        # Persist Docker configuration
        docker_config = DockerConfiguration(
            envConfigId=config_id,
            baseImage=base_image,
            workdir="/app",
            exposedPorts=exposed_ports,
            additionalCommands=additional_commands,
            generatedContent=dockerfile_content
        )
        self.store.save_docker_config(docker_config)

        # Write Dockerfile
        dockerfile_path = Path(project_path) / "Dockerfile"
        with open(dockerfile_path, 'w') as f:
            f.write(dockerfile_content)

        return str(dockerfile_path)


class CreateVirtualEnvironmentFlow:
    """
    FLOW: CreateVirtualEnvironment
    Creates and activates a Python virtual environment with configured settings.
    """

    @staticmethod
    def execute(
        config: VirtualEnvConfig,
        python_path: str,
        requirements_path: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Create virtual environment.

        Returns:
            Dictionary with activation instructions and paths
        """
        env_path = Path(config.projectPath) / config.envName

        # Create virtual environment
        try:
            subprocess.run(
                [python_path, "-m", "venv", str(env_path)],
                check=True,
                capture_output=True
            )
        except subprocess.CalledProcessError as e:
            raise FlowError(f"Failed to create virtual environment: {e.stderr.decode()}")

        # Verify environment was created
        if not env_path.exists():
            raise FlowError(f"Virtual environment directory not created at {env_path}")

        # Determine activation script based on OS
        if sys.platform == "win32":
            activate_script = env_path / "Scripts" / "activate.bat"
        else:
            activate_script = env_path / "bin" / "activate"

        # Install requirements if specified
        if requirements_path and config.includeRequirements:
            pip_path = env_path / "bin" / "pip" if sys.platform != "win32" else env_path / "Scripts" / "pip.exe"
            try:
                subprocess.run(
                    [str(pip_path), "install", "-r", requirements_path],
                    check=True,
                    capture_output=True
                )
            except subprocess.CalledProcessError as e:
                # Non-fatal - environment is still created
                print(f"Warning: Failed to install requirements: {e.stderr.decode()}")

        # Create .python-version file
        python_version_file = Path(config.projectPath) / ".python-version"
        with open(python_version_file, 'w') as f:
            f.write(config.pythonVersion + '\n')

        return {
            "env_path": str(env_path),
            "activate_script": str(activate_script),
            "python_version_file": str(python_version_file),
            "activation_command": f"source {activate_script}" if sys.platform != "win32" else str(activate_script)
        }


class LaunchAIAssistantFlow:
    """
    FLOW: LaunchAIAssistant
    Launches selected AI CLI tool with context about the environment setup.
    """

    def __init__(self, store: JSONStore):
        self.store = store

    def execute(
        self,
        config: VirtualEnvConfig,
        ai_tool: AIToolName,
        custom_prompt: str
    ) -> Tuple[bool, str, Optional[UUID]]:
        """
        Launch AI tool with context.

        Returns:
            (success: bool, message: str, session_id: UUID)
        """
        # Build context prompt
        packages = self.store.get_packages_for_config(config.id)
        package_list = ", ".join([p.packageName for p in packages]) if packages else "none"

        context_prompt = f"""
Python Virtual Environment Setup Context:
- Environment Name: {config.envName}
- Python Version: {config.pythonVersion}
- Project Path: {config.projectPath}
- Packages: {package_list}
- Docker: {'Yes' if config.includeDockerfile else 'No'}

User Request: {custom_prompt}
"""

        # Persist AI session
        session = AIToolSession(
            envConfigId=config.id,
            toolName=ai_tool,
            contextPrompt=context_prompt,
            status=AISessionStatus.INITIATED
        )
        self.store.save_ai_session(session)

        # Check tool availability and get launch command
        tool_commands = {
            AIToolName.CLAUDE_CODE: "claude",
            AIToolName.COPILOT_CLI: "github-copilot-cli",
            AIToolName.CHATGPT_CLI: "chatgpt",
            AIToolName.CURSOR_AI: "cursor"
        }

        if ai_tool not in tool_commands:
            return (False, f"AI tool {ai_tool} not supported", session.id)

        command = tool_commands[ai_tool]

        # Check if tool is available
        try:
            subprocess.run(
                ["which", command],
                check=True,
                capture_output=True
            )
        except subprocess.CalledProcessError:
            return (
                False,
                f"{ai_tool} not found. Please install it first.",
                session.id
            )

        # Update session status
        session.status = AISessionStatus.ACTIVE
        self.store.save_ai_session(session)

        message = f"""
AI Tool: {ai_tool}
Session ID: {session.id}

Context prepared. Launch command:
  {command}

Provide this context to the AI tool:
{context_prompt}
"""

        return (True, message, session.id)
