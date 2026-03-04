"""
Simple JSON-based persistence layer for storing configurations.
No database required - uses local file storage.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional
from uuid import UUID
from .models import (
    VirtualEnvConfig,
    PackageRequirement,
    DockerConfiguration,
    AIToolSession
)


class JSONStore:
    """Simple JSON file-based storage for project data."""

    def __init__(self, storage_path: str = ".pyenv-cli"):
        """Initialize storage in project directory."""
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)

        self.configs_file = self.storage_path / "configs.json"
        self.packages_file = self.storage_path / "packages.json"
        self.docker_file = self.storage_path / "docker.json"
        self.sessions_file = self.storage_path / "ai_sessions.json"

    def _load_json(self, file_path: Path) -> Dict:
        """Load JSON data from file."""
        if not file_path.exists():
            return {}
        with open(file_path, 'r') as f:
            return json.load(f)

    def _save_json(self, file_path: Path, data: Dict):
        """Save JSON data to file."""
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)

    # VirtualEnvConfig operations
    def save_config(self, config: VirtualEnvConfig):
        """Persist VirtualEnvConfig."""
        configs = self._load_json(self.configs_file)
        configs[str(config.id)] = config.model_dump(mode='json')
        self._save_json(self.configs_file, configs)

    def get_config(self, config_id: UUID) -> Optional[VirtualEnvConfig]:
        """Retrieve VirtualEnvConfig by ID."""
        configs = self._load_json(self.configs_file)
        data = configs.get(str(config_id))
        return VirtualEnvConfig(**data) if data else None

    def list_configs(self) -> List[VirtualEnvConfig]:
        """List all VirtualEnvConfigs."""
        configs = self._load_json(self.configs_file)
        return [VirtualEnvConfig(**data) for data in configs.values()]

    # PackageRequirement operations
    def save_package(self, package: PackageRequirement):
        """Persist PackageRequirement."""
        packages = self._load_json(self.packages_file)
        packages[str(package.id)] = package.model_dump(mode='json')
        self._save_json(self.packages_file, packages)

    def get_packages_for_config(self, config_id: UUID) -> List[PackageRequirement]:
        """Get all packages for a specific config."""
        packages = self._load_json(self.packages_file)
        return [
            PackageRequirement(**data)
            for data in packages.values()
            if data['envConfigId'] == str(config_id)
        ]

    def delete_package(self, package_id: UUID):
        """Remove a package requirement."""
        packages = self._load_json(self.packages_file)
        packages.pop(str(package_id), None)
        self._save_json(self.packages_file, packages)

    # DockerConfiguration operations
    def save_docker_config(self, docker: DockerConfiguration):
        """Persist DockerConfiguration."""
        configs = self._load_json(self.docker_file)
        configs[str(docker.id)] = docker.model_dump(mode='json')
        self._save_json(self.docker_file, configs)

    def get_docker_config(self, config_id: UUID) -> Optional[DockerConfiguration]:
        """Get Docker config for a specific env config."""
        configs = self._load_json(self.docker_file)
        for data in configs.values():
            if data['envConfigId'] == str(config_id):
                return DockerConfiguration(**data)
        return None

    # AIToolSession operations
    def save_ai_session(self, session: AIToolSession):
        """Persist AIToolSession."""
        sessions = self._load_json(self.sessions_file)
        sessions[str(session.id)] = session.model_dump(mode='json')
        self._save_json(self.sessions_file, sessions)

    def get_sessions_for_config(self, config_id: UUID) -> List[AIToolSession]:
        """Get all AI sessions for a specific config."""
        sessions = self._load_json(self.sessions_file)
        return [
            AIToolSession(**data)
            for data in sessions.values()
            if data['envConfigId'] == str(config_id)
        ]
