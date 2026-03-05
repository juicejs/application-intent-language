"""
Python version installation helpers.
Supports multiple package managers across different platforms.
"""

import platform
import subprocess
from typing import Tuple, Optional, List
from enum import Enum


class PackageManager(str, Enum):
    """Supported package managers for Python installation."""
    HOMEBREW = "homebrew"  # macOS
    APT = "apt"  # Debian/Ubuntu
    DNF = "dnf"  # Fedora/RHEL
    YUM = "yum"  # CentOS/older RHEL
    PACMAN = "pacman"  # Arch Linux
    ZYPPER = "zypper"  # openSUSE
    PYENV = "pyenv"  # Cross-platform Python version manager
    ASDF = "asdf"  # Cross-platform version manager
    MANUAL = "manual"  # Download from python.org


class PythonInstaller:
    """Helper class for installing Python versions."""

    @staticmethod
    def detect_available_managers() -> List[PackageManager]:
        """
        Detect which package managers are available on the system.

        Returns:
            List of available package managers
        """
        available = []

        # Check for version managers (preferred)
        if PythonInstaller._command_exists("pyenv"):
            available.append(PackageManager.PYENV)

        if PythonInstaller._command_exists("asdf"):
            available.append(PackageManager.ASDF)

        # Check for system package managers
        system = platform.system()

        if system == "Darwin":  # macOS
            if PythonInstaller._command_exists("brew"):
                available.append(PackageManager.HOMEBREW)

        elif system == "Linux":
            if PythonInstaller._command_exists("apt-get"):
                available.append(PackageManager.APT)

            if PythonInstaller._command_exists("dnf"):
                available.append(PackageManager.DNF)

            if PythonInstaller._command_exists("yum"):
                available.append(PackageManager.YUM)

            if PythonInstaller._command_exists("pacman"):
                available.append(PackageManager.PACMAN)

            if PythonInstaller._command_exists("zypper"):
                available.append(PackageManager.ZYPPER)

        # Manual installation is always available
        available.append(PackageManager.MANUAL)

        return available

    @staticmethod
    def _command_exists(command: str) -> bool:
        """Check if a command exists in PATH."""
        try:
            subprocess.run(
                ["which", command],
                capture_output=True,
                check=True,
                timeout=2
            )
            return True
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
            return False

    @staticmethod
    def get_install_command(
        manager: PackageManager,
        python_version: str
    ) -> Tuple[str, List[str]]:
        """
        Get the installation command for a specific package manager.

        Returns:
            (description: str, command_parts: List[str])
        """
        version_parts = python_version.split('.')
        major_minor = f"{version_parts[0]}.{version_parts[1]}"

        commands = {
            PackageManager.PYENV: (
                f"Install Python {python_version} using pyenv",
                ["pyenv", "install", python_version]
            ),
            PackageManager.ASDF: (
                f"Install Python {python_version} using asdf",
                ["asdf", "plugin", "add", "python", "&&", "asdf", "install", "python", python_version]
            ),
            PackageManager.HOMEBREW: (
                f"Install Python {major_minor} using Homebrew",
                ["brew", "install", f"python@{major_minor}"]
            ),
            PackageManager.APT: (
                f"Install Python {major_minor} using apt",
                ["sudo", "apt-get", "update", "&&", "sudo", "apt-get", "install", "-y", f"python{major_minor}", f"python{major_minor}-venv"]
            ),
            PackageManager.DNF: (
                f"Install Python {major_minor} using dnf",
                ["sudo", "dnf", "install", "-y", f"python{major_minor}"]
            ),
            PackageManager.YUM: (
                f"Install Python {major_minor} using yum",
                ["sudo", "yum", "install", "-y", f"python{major_minor}"]
            ),
            PackageManager.PACMAN: (
                f"Install Python {major_minor} using pacman",
                ["sudo", "pacman", "-S", f"python{major_minor.replace('.', '')}"]
            ),
            PackageManager.ZYPPER: (
                f"Install Python {major_minor} using zypper",
                ["sudo", "zypper", "install", "-y", f"python{major_minor}"]
            ),
            PackageManager.MANUAL: (
                f"Download Python {python_version} from python.org",
                []  # No command - user must download manually
            )
        }

        return commands.get(manager, ("Unknown package manager", []))

    @staticmethod
    def install_python(
        manager: PackageManager,
        python_version: str,
        interactive: bool = True
    ) -> Tuple[bool, str]:
        """
        Install Python using the specified package manager.

        Args:
            manager: Package manager to use
            python_version: Python version to install
            interactive: Whether to run in interactive mode

        Returns:
            (success: bool, message: str)
        """
        if manager == PackageManager.MANUAL:
            version_parts = python_version.split('.')
            major_minor = f"{version_parts[0]}.{version_parts[1]}"
            url = f"https://www.python.org/downloads/release/python-{python_version.replace('.', '')}/"
            return (
                False,
                f"Please download Python {major_minor} manually from:\n{url}\n"
                f"Then follow the installation instructions for your platform."
            )

        description, cmd_parts = PythonInstaller.get_install_command(manager, python_version)

        if not cmd_parts:
            return (False, "No installation command available")

        # Build command string
        cmd_string = " ".join(cmd_parts)

        if interactive:
            return (
                False,
                f"Run this command to install:\n\n{cmd_string}\n\n"
                f"Then restart the application."
            )

        # Non-interactive installation (requires sudo in many cases)
        try:
            # For commands with && we need to use shell=True
            if "&&" in cmd_string:
                result = subprocess.run(
                    cmd_string,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minutes max
                )
            else:
                result = subprocess.run(
                    cmd_parts,
                    capture_output=True,
                    text=True,
                    timeout=300
                )

            if result.returncode == 0:
                return (True, f"Successfully installed Python {python_version}")
            else:
                return (False, f"Installation failed: {result.stderr}")

        except subprocess.TimeoutExpired:
            return (False, "Installation timed out (exceeded 5 minutes)")
        except Exception as e:
            return (False, f"Installation error: {str(e)}")

    @staticmethod
    def get_installation_url(python_version: str) -> str:
        """Get the python.org download URL for manual installation."""
        version_parts = python_version.split('.')
        major_minor = f"{version_parts[0]}.{version_parts[1]}"
        version_number = python_version.replace('.', '')

        return f"https://www.python.org/downloads/release/python-{version_number}/"
