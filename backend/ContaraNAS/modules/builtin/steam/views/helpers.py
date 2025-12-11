from datetime import datetime
import os
from pathlib import Path


def format_bytes(bytes_value: int) -> str:
    """Format bytes as human readable strings"""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if abs(bytes_value) < 1024:
            return f"{bytes_value:.1f} {unit}"

        bytes_value /= 1024

    return f"{bytes_value:.1f} PB"


def convert_date_to_string(int_timestamp: int) -> str:
    """Convert integer timestamps to human readable date strings"""
    if int_timestamp <= 0:
        return "Never"

    date = datetime.fromtimestamp(int_timestamp)
    delta = (datetime.now() - date).days

    if delta < 7:
        return {0: "Today", 1: "Yesterday"}.get(delta, f"{delta} days ago")

    if delta < 30:
        weeks = delta // 7
        return "Last week" if weeks == 1 else f"{weeks} weeks ago"

    if delta < 365:
        months = delta // 30
        return "Last month" if months == 1 else f"{months} months ago"

    return date.strftime("%b %d, %Y")


def get_mountpoint(path: str) -> str:
    """Get the mountpoint for a given path"""
    p = Path(path).resolve()

    # Windows: just return the drive
    if os.name == "nt":
        return p.drive + "/"

    # Unix: walk up the tree until we find the mount point
    while not p.is_mount() and p != p.parent:
        p = p.parent

    return str(p)
