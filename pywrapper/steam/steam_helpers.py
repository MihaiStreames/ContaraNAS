import os
import requests

def check_url(url):
    """
    Verifies if a game's store page URL exists by performing an HTTP HEAD request.

    Args:
        url (str): URL of the game's store page to check.

    Returns:
        bool: True if the URL exists and does not redirect to the Steam store homepage, False otherwise.
    """
    try:
        response = requests.head(url, allow_redirects=True, timeout=5)
        final_url = response.url
        return final_url != "https://store.steampowered.com/"
    except requests.RequestException:
        return False


def parse_output(entry_id, data):
    """
    Returns DLC name if entry_id is a DLC ID, or Depot name if it's a Depot ID.

    Args:
        entry_id (str): ID to search for (either DLC ID or Depot ID).
        data (dict): Dictionary with 'dlc' and 'depots' from SteamDB.

    Returns:
        str: The name of the DLC or the depot name.
    """
    for dlc in data.get("dlc", []):
        if dlc["dlc_id"] == entry_id:
            return dlc["name"]

    for depot in data.get("depots", []):
        if depot["depot_id"] == entry_id:
            return depot["details"].split("|")[-1].strip()

    return f"ID {entry_id} not found"

def format_size(size_in_bytes):
    """
    Converts a size in bytes into a human-readable format (GB, MB, KB, or B).

    Args:
        size_in_bytes (int): Size in bytes.

    Returns:
        str: Formatted size string.
    """
    if size_in_bytes >= 1024 ** 3:
        return f"{size_in_bytes / (1024 ** 3):.2f} GB"
    elif size_in_bytes >= 1024 ** 2:
        return f"{size_in_bytes / (1024 ** 2):.2f} MB"
    elif size_in_bytes >= 1024:
        return f"{size_in_bytes / 1024:.2f} KB"
    else:
        return f"{size_in_bytes} B"

def get_size(path):
    """
    Calculates the total size of all files in a directory recursively.

    Args:
        path (str): Directory path.

    Returns:
        int: Total size in bytes.
    """
    total_size = 0
    for root, _, files in os.walk(path):
        total_size += sum(os.path.getsize(os.path.join(root, f)) for f in files)
    return total_size