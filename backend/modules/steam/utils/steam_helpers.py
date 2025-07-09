import os

import requests


def check_url(url: str) -> bool:
    """Check if the given URL is valid and doesn't redirect to the default Steam store page"""
    try:
        response = requests.head(url, allow_redirects=True, timeout=5)
        final_url = response.url
        return final_url != "https://store.steampowered.com/"
    except requests.RequestException:
        return False


def get_size(directory: str) -> int:
    """Calculate the total size of files in a directory"""
    total_size = 0
    for root, _, files in os.walk(directory):
        total_size += sum(os.path.getsize(os.path.join(root, f)) for f in files)
    return total_size
