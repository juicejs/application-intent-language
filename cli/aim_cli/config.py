#!/usr/bin/env python3
"""
Config management for AIM CLI
Handles aim.config.json in project root
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional


DEFAULT_CONFIG = {
    "version": "1.0",
    "stack": {
        "frontend": "Next.js",
        "backend": "Node.js",
        "database": "PostgreSQL"
    },
    "registry": "https://intentmodel.dev/registry-files/index.json",
    "outputDir": "aim"
}


def get_config_path() -> Path:
    """Get path to config file (./aim.config.json)"""
    return Path.cwd() / "aim.config.json"


def load_config() -> Dict[str, Any]:
    """Load config from aim.config.json or return defaults"""
    config_path = get_config_path()

    if not config_path.exists():
        return DEFAULT_CONFIG.copy()

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        # Merge with defaults to ensure all keys exist
        merged = DEFAULT_CONFIG.copy()
        merged.update(config)

        # Deep merge stack if it exists
        if 'stack' in config:
            merged['stack'] = {**DEFAULT_CONFIG['stack'], **config['stack']}

        return merged
    except (json.JSONDecodeError, IOError) as e:
        # Return defaults if config is invalid
        return DEFAULT_CONFIG.copy()


def save_config(config: Dict[str, Any]) -> None:
    """Save config to aim.config.json"""
    config_path = get_config_path()

    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)


def init_config() -> bool:
    """Create default config file if it doesn't exist"""
    config_path = get_config_path()

    if config_path.exists():
        return False  # Already exists

    save_config(DEFAULT_CONFIG)
    return True  # Created new file


def get_config_value(config: Dict[str, Any], key: str) -> Optional[Any]:
    """Get a config value using dot notation (e.g., 'stack.frontend')"""
    keys = key.split('.')
    value = config

    for k in keys:
        if isinstance(value, dict) and k in value:
            value = value[k]
        else:
            return None

    return value


def set_config_value(config: Dict[str, Any], key: str, value: str) -> Dict[str, Any]:
    """Set a config value using dot notation (e.g., 'stack.frontend', 'React')"""
    keys = key.split('.')
    current = config

    # Navigate to the parent of the target key
    for k in keys[:-1]:
        if k not in current:
            current[k] = {}
        current = current[k]

    # Set the value
    current[keys[-1]] = value

    return config
