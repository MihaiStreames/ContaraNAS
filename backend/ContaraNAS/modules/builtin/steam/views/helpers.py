from datetime import datetime
import os
from pathlib import Path


def format_bytes(bytes_value: int) -> str:
    """Format bytes as human readable string"""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if abs(bytes_value) < 1024:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024
    return f"{bytes_value:.1f} PB"


def convert_date_to_string(int_timestamp: int) -> str:
    # 1625079600 -> "Jun 30, 2021"
    if int_timestamp <= 0:
        return "Never"

    date = datetime.fromtimestamp(int_timestamp)
    now = datetime.now()
    delta = now - date

    if delta.days == 0:
        return "Today"
    if delta.days == 1:
        return "Yesterday"
    if delta.days < 7:
        return f"{delta.days} days ago"
    if delta.days < 30:
        weeks = delta.days // 7
        return f"{weeks} week{'s' if weeks > 1 else ''} ago"
    if delta.days < 365:
        months = delta.days // 30
        return f"{months} month{'s' if months > 1 else ''} ago"
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
