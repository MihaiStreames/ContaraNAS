import json
from pathlib import Path
import platform
from typing import Any

from ContaraNAS.core.utils.logger import get_logger


logger = get_logger(__name__)


def load_json(file_path: Path) -> dict | None:
    """Load JSON data from a file

    Args:
        file_path: Path to the JSON file to load

    Returns:
        Loaded JSON data as dict, or None if file doesn't exist or on error
    """
    try:
        if not Path(file_path).exists():
            logger.debug(f"JSON file not found: {file_path}")
            return None

        with Path.open(file_path, encoding="utf-8") as f:
            data = json.load(f)
            logger.debug(f"Loaded JSON from {file_path}")
            return data

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON from {file_path}: {e}")
        return None
    except (OSError, PermissionError) as e:
        logger.error(f"Failed to read file {file_path}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error loading JSON from {file_path}: {e}")
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
        # Ensure parent directory exists
        parent_dir = Path(file_path).parent
        parent_dir.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Ensured directory exists: {parent_dir}")

        # Write JSON data
        with Path.open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        logger.debug(f"Saved JSON to {file_path}")

    except (OSError, PermissionError) as e:
        logger.error(f"Failed to write file {file_path}: {e}")
        raise
    except TypeError as e:
        logger.error(f"Data not JSON serializable for {file_path}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error saving JSON to {file_path}: {e}")
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
