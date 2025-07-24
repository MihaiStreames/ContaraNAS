import platform
import re
import shutil
import subprocess
from pathlib import Path
from typing import Union, Dict

import requests


def check_url(url: str) -> bool:
    """Check if the given URL is valid and doesn't redirect to the default Steam store page"""
    try:
        response = requests.head(url, allow_redirects=True)
        final_url = response.url
        return final_url != "https://store.steampowered.com/"
    except requests.RequestException:
        return False


def get_dir_size(directory: Union[str, Path]) -> int | None:
    """Calculate the total size of files in a directory"""
    system = platform.system()

    if system in ['Linux', 'Darwin']:
        return _get_dir_size_unix(directory)
    elif system == 'Windows':
        return _get_dir_size_win(directory)
    return None


def _get_dir_size_unix(directory: Union[str, Path]) -> int:
    """Calculate directory size for Unix-like systems"""
    result = subprocess.run(['du', '-sb', directory], capture_output=True, text=True, check=True)
    size_bytes = int(result.stdout.split()[0])
    return size_bytes


def _get_dir_size_win(directory: Union[str, Path]) -> int | None:
    """Get directory size using dir command (Windows)"""
    result = subprocess.run(['dir', directory, '/s', '/-c'], capture_output=True, text=True, shell=True, check=True)
    lines = result.stdout.split('\n')

    for line in reversed(lines):
        if 'bytes' in line and 'Total Files Listed:' in line:
            # Extract number before "bytes"
            match = re.search(r'([\d,]+) bytes', line)
            if match:
                return int(match.group(1).replace(',', ''))
    return None


def is_manifest_file(path: str) -> bool:
    """Check if the path is a Steam manifest file"""
    if not path.endswith('.acf'):
        return False
    filename = Path(path).name
    return filename.startswith('appmanifest_')


def extract_app_id(manifest_path: Path) -> str | None:
    """Extract Steam App ID from manifest file path"""
    # appmanifest_1942280.acf -> 1942280
    filename = manifest_path.name
    if filename.startswith('appmanifest_') and filename.endswith('.acf'):
        return filename[12:-4]  # Remove 'appmanifest_' and '.acf'
    return None


def get_drive_info(path: Path) -> Dict[str, int]:
    """Get drive size information for a path"""
    stat = shutil.disk_usage(path)
    return {
        "total": stat.total,
        "free": stat.free,
        "used": stat.total - stat.free
    }
