"""
Platform-specific path utilities for cache and data directories.
"""

import platform
from pathlib import Path


def get_app_cache_dir() -> Path:
    """
    Get the platform-specific cache directory for the application.

    Returns:
        Path: Platform-specific cache directory
            - macOS: ~/Library/Caches/pokemon-card-generator/
            - Linux: ~/.cache/pokemon-card-generator/
            - Windows: %LOCALAPPDATA%\\pokemon-card-generator\\Cache\\
    """
    app_name = "pokemon-card-generator"
    system = platform.system()

    if system == "Darwin":  # macOS
        base_dir = Path.home() / "Library" / "Caches"
    elif system == "Windows":
        import os
        local_app_data = os.getenv("LOCALAPPDATA")
        if local_app_data:
            base_dir = Path(local_app_data)
        else:
            # Fallback to user profile
            base_dir = Path.home() / "AppData" / "Local"
        return base_dir / app_name / "Cache"
    else:  # Linux and others
        xdg_cache = Path.home() / ".cache"
        base_dir = xdg_cache

    return base_dir / app_name


def get_app_data_dir() -> Path:
    """
    Get the platform-specific data directory for the application.

    Returns:
        Path: Platform-specific data directory
            - macOS: ~/Library/Application Support/pokemon-card-generator/
            - Linux: ~/.local/share/pokemon-card-generator/
            - Windows: %APPDATA%\\pokemon-card-generator\\
    """
    app_name = "pokemon-card-generator"
    system = platform.system()

    if system == "Darwin":  # macOS
        base_dir = Path.home() / "Library" / "Application Support"
    elif system == "Windows":
        import os
        app_data = os.getenv("APPDATA")
        if app_data:
            base_dir = Path(app_data)
        else:
            # Fallback to user profile
            base_dir = Path.home() / "AppData" / "Roaming"
        return base_dir / app_name
    else:  # Linux and others
        xdg_data = Path.home() / ".local" / "share"
        base_dir = xdg_data

    return base_dir / app_name
