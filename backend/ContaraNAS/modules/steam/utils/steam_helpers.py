import asyncio
from pathlib import Path
import platform
import re
import shutil
import subprocess


def is_manifest_file(path: str) -> bool:
    """Check if the path is a Steam manifest file"""
    if not path.endswith(".acf"):
        return False
    filename = Path(path).name
    return filename.startswith("appmanifest_")


def extract_app_id(manifest_path: Path) -> str | None:
    """Extract Steam App ID from manifest file path"""
    # appmanifest_1942280.acf -> 1942280
    filename = manifest_path.name
    if filename.startswith("appmanifest_") and filename.endswith(".acf"):
        return filename[12:-4]  # Remove 'appmanifest_' and '.acf'
    return None


def get_drive_info(path: Path) -> dict[str, int]:
    """Get drive size information for a path"""
    stat = shutil.disk_usage(path)
    return {"total": stat.total, "free": stat.free, "used": stat.total - stat.free}


def _get_dir_size_unix(directory: str | Path) -> int:
    """Calculate directory size for Unix-like systems"""
    result = subprocess.run(["du", "-sb", directory], capture_output=True, text=True, check=True)
    return int(result.stdout.split()[0])


def _get_dir_size_win(directory: str | Path) -> int | None:
    """Get directory size using dir command (Windows)"""
    result = subprocess.run(
        ["dir", directory, "/s", "/-c"],
        capture_output=True,
        text=True,
        shell=True,
        check=True,
    )
    lines = result.stdout.split("\n")

    for line in reversed(lines):
        if "bytes" in line and "Total Files Listed:" in line:
            # Extract number before "bytes"
            match = re.search(r"([\d,]+) bytes", line)
            if match:
                return int(match.group(1).replace(",", ""))
    return None


async def get_dir_size(directory: str | Path) -> int | None:
    """Calculate the total size of files in a directory (async)

    Runs the blocking subprocess operation in a thread pool to avoid blocking the event loop.
    """

    def _sync_get_dir_size() -> int | None:
        system = platform.system()
        if system in ["Linux", "Darwin"]:
            return _get_dir_size_unix(directory)
        if system == "Windows":
            return _get_dir_size_win(directory)
        return None

    return await asyncio.to_thread(_sync_get_dir_size)
