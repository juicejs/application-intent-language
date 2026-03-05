"""
CONTRACT layer - Application boundary and use cases.
Implements strict input validation, authorization, and orchestrates FLOW execution.
"""

from typing import Dict, List, Optional, Tuple
from uuid import UUID

from .models import (
    VirtualEnvConfig,
    PackageRequirement,
    AIToolName
)
from .persistence import JSONStore
from .flows import (
    ValidatePythonVersionFlow,
    GenerateRequirementsListFlow,
    GenerateDockerfileFlow,
    CreateVirtualEnvironmentFlow,
    LaunchAIAssistantFlow,
    FlowError
)


class ContractError(Exception):
    """Exception raised for contract validation or execution failures."""
    pass


class CreateVirtualEnvContract:
    """
    CONTRACT: CreateVirtualEnv
    Main contract for creating a Python virtual environment with all configurations.
    """

    def __init__(self, store: JSONStore):
        self.store = store

    def execute(
        self,
        env_name: str,
        python_version: str,
        project_path: str,
        include_dockerfile: bool = False,
        include_requirements: bool = True,
        ai_tool_preference: Optional[str] = None
    ) -> Dict:
        """
        Execute virtual environment creation workflow.

        INPUT validation:
            - env_name: required, filesystem-safe
            - python_version: required, valid version pattern
            - project_path: required, valid directory
            - include_dockerfile: boolean
            - include_requirements: boolean

        LOGIC:
            - EXECUTE Flow.ValidatePythonVersion
            - PERSIST Schema.VirtualEnvConfig
            - IF includeRequirements: EXECUTE Flow.GenerateRequirementsList
            - IF includeDockerfile: EXECUTE Flow.GenerateDockerfile
            - EXECUTE Flow.CreateVirtualEnvironment
            - RETURN activation instructions and file paths

        Returns:
            Dict with success status, config_id, activation instructions, and file paths
        """
        # INPUT VALIDATION
        if not env_name or not env_name.strip():
            raise ContractError("Environment name is required")

        if not python_version or not python_version.strip():
            raise ContractError("Python version is required")

        if not project_path or not project_path.strip():
            raise ContractError("Project path is required")

        # EXPECTS: project_path exists
        import os
        if not os.path.exists(project_path):
            raise ContractError(f"Project path does not exist: {project_path}")

        # STEP 1: EXECUTE Flow.ValidatePythonVersion
        success, python_path, error = ValidatePythonVersionFlow.execute(python_version)
        if not success:
            raise ContractError(error)

        # STEP 2: PERSIST Schema.VirtualEnvConfig
        try:
            config = VirtualEnvConfig(
                envName=env_name,
                pythonVersion=python_version,
                projectPath=project_path,
                includeDockerfile=include_dockerfile,
                includeRequirements=include_requirements,
                aiToolPreference=AIToolName(ai_tool_preference) if ai_tool_preference else None
            )
        except ValueError as e:
            raise ContractError(f"Invalid configuration: {str(e)}")

        self.store.save_config(config)

        result = {
            "success": True,
            "config_id": str(config.id),
            "env_name": config.envName,
            "files_generated": []
        }

        requirements_path = None

        # STEP 3: IF includeRequirements: EXECUTE Flow.GenerateRequirementsList
        if include_requirements:
            try:
                req_flow = GenerateRequirementsListFlow(self.store)
                requirements_path = req_flow.execute(config.id, project_path)
                result["files_generated"].append(requirements_path)
            except Exception as e:
                # Non-fatal - continue with empty requirements
                print(f"Warning: Could not generate requirements.txt: {str(e)}")

        # STEP 4: IF includeDockerfile: EXECUTE Flow.GenerateDockerfile
        if include_dockerfile:
            try:
                docker_flow = GenerateDockerfileFlow(self.store)
                dockerfile_path = docker_flow.execute(config.id, python_version, project_path)
                result["files_generated"].append(dockerfile_path)
            except Exception as e:
                raise ContractError(f"Failed to generate Dockerfile: {str(e)}")

        # STEP 5: EXECUTE Flow.CreateVirtualEnvironment
        try:
            env_result = CreateVirtualEnvironmentFlow.execute(
                config,
                python_path,
                requirements_path
            )
            result.update(env_result)
        except FlowError as e:
            raise ContractError(f"Failed to create virtual environment: {str(e)}")

        return result


class ConfigurePackagesContract:
    """
    CONTRACT: ConfigurePackages
    Configures Python package dependencies for the environment.
    """

    def __init__(self, store: JSONStore):
        self.store = store

    def execute(
        self,
        env_config_id: str,
        packages: List[Dict[str, str]]
    ) -> Dict:
        """
        Configure package dependencies.

        INPUT:
            - envConfigId: required, must exist
            - packages: array of {name: str, version: str}

        LOGIC:
            - VALIDATE envConfigId exists
            - EXECUTE Flow.GenerateRequirementsList
            - RETURN requirements.txt path and content preview

        Returns:
            Dict with requirements file path and package list
        """
        # VALIDATE envConfigId exists
        try:
            config_uuid = UUID(env_config_id)
        except ValueError:
            raise ContractError("Invalid config ID format")

        config = self.store.get_config(config_uuid)
        if not config:
            raise ContractError(f"Configuration {env_config_id} not found")

        # Clear existing packages for this config
        existing_packages = self.store.get_packages_for_config(config_uuid)
        for pkg in existing_packages:
            self.store.delete_package(pkg.id)

        # Add new packages
        for pkg_data in packages:
            try:
                package = PackageRequirement(
                    envConfigId=config_uuid,
                    packageName=pkg_data.get("name", ""),
                    versionSpec=pkg_data.get("version")
                )
                self.store.save_package(package)
            except ValueError as e:
                raise ContractError(f"Invalid package specification: {str(e)}")

        # Generate requirements.txt
        req_flow = GenerateRequirementsListFlow(self.store)
        requirements_path = req_flow.execute(config_uuid, config.projectPath)

        return {
            "success": True,
            "requirements_path": requirements_path,
            "packages_count": len(packages)
        }


class ConfigureDockerContract:
    """
    CONTRACT: ConfigureDocker
    Configures and generates Dockerfile for the Python environment.
    """

    def __init__(self, store: JSONStore):
        self.store = store

    def execute(
        self,
        env_config_id: str,
        exposed_ports: Optional[List[int]] = None,
        additional_commands: Optional[List[str]] = None
    ) -> Dict:
        """
        Configure Docker setup.

        INPUT:
            - envConfigId: required, must exist
            - exposedPorts: optional list of ports
            - additionalCommands: optional list of Docker commands

        LOGIC:
            - VALIDATE envConfigId exists
            - EXECUTE Flow.GenerateDockerfile
            - RETURN Dockerfile path and build instructions

        Returns:
            Dict with Dockerfile path and build instructions
        """
        # VALIDATE envConfigId exists
        try:
            config_uuid = UUID(env_config_id)
        except ValueError:
            raise ContractError("Invalid config ID format")

        config = self.store.get_config(config_uuid)
        if not config:
            raise ContractError(f"Configuration {env_config_id} not found")

        # Generate Dockerfile
        docker_flow = GenerateDockerfileFlow(self.store)
        dockerfile_path = docker_flow.execute(
            config_uuid,
            config.pythonVersion,
            config.projectPath,
            exposed_ports,
            additional_commands
        )

        return {
            "success": True,
            "dockerfile_path": dockerfile_path,
            "build_command": f"docker build -t {config.envName} .",
            "run_command": f"docker run -it {config.envName}"
        }


class PromptAIToolContract:
    """
    CONTRACT: PromptAITool
    Launches an AI CLI tool with context about the Python environment.
    """

    def __init__(self, store: JSONStore):
        self.store = store

    def execute(
        self,
        env_config_id: str,
        ai_tool_name: str,
        custom_prompt: str = ""
    ) -> Dict:
        """
        Launch AI tool with environment context.

        INPUT:
            - envConfigId: required, must exist
            - aiToolName: required, must be supported
            - customPrompt: optional user message

        LOGIC:
            - VALIDATE aiToolName is supported
            - LOAD Schema.VirtualEnvConfig by envConfigId
            - EXECUTE Flow.LaunchAIAssistant
            - RETURN session info and tool status

        Returns:
            Dict with session ID and launch instructions
        """
        # VALIDATE envConfigId exists
        try:
            config_uuid = UUID(env_config_id)
        except ValueError:
            raise ContractError("Invalid config ID format")

        config = self.store.get_config(config_uuid)
        if not config:
            raise ContractError(f"Configuration {env_config_id} not found")

        # VALIDATE aiToolName is supported
        try:
            ai_tool = AIToolName(ai_tool_name)
        except ValueError:
            raise ContractError(
                f"Unsupported AI tool: {ai_tool_name}. "
                f"Supported tools: {', '.join([t.value for t in AIToolName])}"
            )

        # EXECUTE Flow.LaunchAIAssistant
        ai_flow = LaunchAIAssistantFlow(self.store)
        success, message, session_id = ai_flow.execute(config, ai_tool, custom_prompt)

        return {
            "success": success,
            "message": message,
            "session_id": str(session_id) if session_id else None,
            "ai_tool": ai_tool_name
        }
