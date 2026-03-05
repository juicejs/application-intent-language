"""
SCHEMA models synthesized from AIM v1.4 specification.
Maps directly to domain entities with strict validation.
"""

from datetime import datetime
from enum import Enum
from typing import Optional, List
from uuid import uuid4, UUID
from pydantic import BaseModel, Field, field_validator
import re


class AIToolName(str, Enum):
    """Enumeration of supported AI CLI tools."""
    CLAUDE_CODE = "claude-code"
    COPILOT_CLI = "copilot-cli"
    CHATGPT_CLI = "chatgpt-cli"
    CURSOR_AI = "cursor-ai"
    NONE = "none"


class AISessionStatus(str, Enum):
    """Enumeration of AI tool session states."""
    INITIATED = "initiated"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"


class VirtualEnvConfig(BaseModel):
    """
    SCHEMA: VirtualEnvConfig
    Represents the configuration for a Python virtual environment to be created.
    """
    id: UUID = Field(default_factory=uuid4)
    envName: str = Field(min_length=1, max_length=100)
    pythonVersion: str
    projectPath: str
    includeDockerfile: bool = False
    includeRequirements: bool = True
    aiToolPreference: Optional[AIToolName] = None
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)

    @field_validator('envName')
    @classmethod
    def validate_env_name(cls, v: str) -> str:
        """Validate environment name is filesystem-safe."""
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Environment name must contain only alphanumeric characters, hyphens, and underscores')
        return v

    @field_validator('pythonVersion')
    @classmethod
    def validate_python_version(cls, v: str) -> str:
        """Validate Python version follows supported pattern."""
        if not re.match(r'^3\.(8|9|10|11|12|13)(\.\d+)?$', v):
            raise ValueError('Python version must be 3.8, 3.9, 3.10, 3.11, 3.12, or 3.13 (with optional patch version)')
        return v

    class Config:
        use_enum_values = True


class PackageRequirement(BaseModel):
    """
    SCHEMA: PackageRequirement
    Represents a single Python package dependency with version constraints.
    """
    id: UUID = Field(default_factory=uuid4)
    envConfigId: UUID
    packageName: str = Field(min_length=1, max_length=100)
    versionSpec: Optional[str] = None
    description: Optional[str] = Field(None, max_length=500)
    addedAt: datetime = Field(default_factory=datetime.utcnow)

    @field_validator('versionSpec')
    @classmethod
    def validate_version_spec(cls, v: Optional[str]) -> Optional[str]:
        """Validate version specifier follows PEP 440 standards."""
        if v is not None and not re.match(r'^([=<>!~]=?)?[0-9]+(\.[0-9]+)*(\.[*])?$', v):
            raise ValueError('Version specifier must follow PEP 440 format')
        return v


class DockerConfiguration(BaseModel):
    """
    SCHEMA: DockerConfiguration
    Represents Docker configuration for the Python environment.
    """
    id: UUID = Field(default_factory=uuid4)
    envConfigId: UUID
    baseImage: str = "python:3.11-slim"
    workdir: str = "/app"
    exposedPorts: Optional[List[int]] = None
    additionalCommands: Optional[List[str]] = None
    generatedContent: str
    createdAt: datetime = Field(default_factory=datetime.utcnow)


class AIToolSession(BaseModel):
    """
    SCHEMA: AIToolSession
    Represents an AI tool interaction session for environment assistance.
    """
    id: UUID = Field(default_factory=uuid4)
    envConfigId: UUID
    toolName: AIToolName
    contextPrompt: str
    startedAt: datetime = Field(default_factory=datetime.utcnow)
    status: AISessionStatus = AISessionStatus.INITIATED

    class Config:
        use_enum_values = True
