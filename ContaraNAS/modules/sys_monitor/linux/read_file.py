from pathlib import Path


def read_file(path: Path) -> str | None:
    with open(path, encoding="utf-8") as file:
        return file.read()
