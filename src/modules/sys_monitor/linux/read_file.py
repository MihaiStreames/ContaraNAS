from pathlib import Path
from typing import Optional


def read_file(path: Path) -> Optional[str]:
    with open(path, "r", encoding="utf-8") as file:
        return file.read()
