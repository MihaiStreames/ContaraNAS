import json
from pathlib import Path
import platform
from typing import Any

from backend.ContaraNAS.core.utils.logger import get_logger


logger = get_logger(__name__)


def load_json(file_path: Path) -> dict[str, Any] | None:
    """Load JSON data from a file

    Args:
        file_path: Path to the JSON file to load

    Returns:
        Loaded JSON data as dict, or None if file doesn't exist or on error
    """
    try:
        if not Path(file_path).exists():
            return None

        with Path(file_path).open(encoding="utf-8") as f:
            data: dict[str, Any] = json.load(f)
            return data

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON from {file_path}: {e}")
        return None
    except (OSError, PermissionError) as e:
        logger.error(f"Failed to read file {file_path}: {e}")
        return None


def save_json(file_path: Path, data: Any) -> None:
    """Save data to a JSON file

    Args:
        file_path: Path where JSON data should be saved
        data: Data to serialize to JSON

    Raises:
        OSError: If directory creation or file writing fails
        TypeError: If data is not JSON serializable
    """
    try:
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        with Path(file_path).open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    except (OSError, PermissionError) as e:
        logger.error(f"Failed to write file {file_path}: {e}")
        raise
    except TypeError as e:
        logger.error(f"Data not JSON serializable for {file_path}: {e}")
        raise


def get_cache_dir() -> Path:
    """Get the appropriate cache directory for the platform"""
    system = platform.system()

    if system == "Linux":
        return Path.home() / ".cache" / "contaranas"

    if system == "Windows":
        return Path.home() / "AppData" / "Local" / "contaranas" / "cache"
    # Unknown platform, fallback to home directory
    return Path.home() / ".contaranas"
