import os
import requests


def check_url(url):
    try:
        response = requests.head(url, allow_redirects=True, timeout=5)
        final_url = response.url
        return final_url != "https://store.steampowered.com/"
    except requests.RequestException:
        return False


def parse_output(entry_id, data):
    for dlc in data.get("dlc", []):
        if dlc["dlc_id"] == entry_id:
            return dlc["name"]

    for depot in data.get("depots", []):
        if depot["depot_id"] == entry_id:
            return depot["details"].split("|")[-1].strip()

    return f"ID {entry_id} not found"

def format_size(size_in_bytes):
    if size_in_bytes >= 1024 ** 3:
        return f"{size_in_bytes / (1024 ** 3):.2f} GB"
    elif size_in_bytes >= 1024 ** 2:
        return f"{size_in_bytes / (1024 ** 2):.2f} MB"
    elif size_in_bytes >= 1024:
        return f"{size_in_bytes / 1024:.2f} KB"
    else:
        return f"{size_in_bytes} B"

def get_size(path):
    total_size = 0
    for root, _, files in os.walk(path):
        total_size += sum(os.path.getsize(os.path.join(root, f)) for f in files)
    return total_size