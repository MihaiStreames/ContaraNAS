import json
import os
from pathlib import Path
from typing import Any, Optional


def load_json(file_path: Path) -> Optional[dict]:
    """Load JSON data from a file"""
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def save_json(file_path: Path, data: Any) -> None:
    """Save data to a JSON file"""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
