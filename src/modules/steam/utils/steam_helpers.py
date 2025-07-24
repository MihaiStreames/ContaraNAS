import os
from pathlib import Path
from typing import Union

import requests


def check_url(url: str) -> bool:
    """Check if the given URL is valid and doesn't redirect to the default Steam store page"""
    try:
        response = requests.head(url, allow_redirects=True)
        final_url = response.url
        return final_url != "https://store.steampowered.com/"
    except requests.RequestException:
        return False


def get_size(directory: Union[str, Path]) -> int:
    """Calculate the total size of files in a directory"""
    total_size = 0
    for root, _, files in os.walk(directory):
        total_size += sum(os.path.getsize(os.path.join(root, f)) for f in files)
    return total_size


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
