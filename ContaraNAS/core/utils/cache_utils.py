import json
import os
from pathlib import Path
import platform
from typing import Any


def load_json(file_path: Path) -> dict | None:
    """Load JSON data from a file"""
    if os.path.exists(file_path):
        with open(file_path, encoding="utf-8") as f:
            return json.load(f)
    return None


def save_json(file_path: Path, data: Any) -> None:
    """Save data to a JSON file"""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def get_cache_dir() -> Path:
    """Get the appropriate cache directory for the platform"""
    system = platform.system()

    if system == "Linux":
        return Path.home() / ".cache" / "contaranas"

    if system == "Windows":
        return Path.home() / "AppData" / "Local" / "contaranas" / "cache"
    # Unknown platform, fallback to home directory
    return Path.home() / ".contaranas"
