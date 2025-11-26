import json
from pathlib import Path
from typing import Any

from backend.ContaraNAS.core.utils.logger import get_logger


logger = get_logger(__name__)


def load_json(file_path: Path) -> dict[str, Any] | None:
    """Load JSON data from a file"""
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
    """Save data to a JSON file"""
    try:
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        with Path(file_path).open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    except (OSError, PermissionError) as e:
        logger.error(f"Failed to write file {file_path}: {e}")
        raise
    except TypeError as e:
        logger.error(f"Data not JSON serializable for {file_path}: {e}")
        raiseF
