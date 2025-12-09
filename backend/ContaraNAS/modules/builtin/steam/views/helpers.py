import os
from pathlib import Path


def format_bytes(bytes_value: int) -> str:
    """Format bytes as human readable string"""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if abs(bytes_value) < 1024:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024
    return f"{bytes_value:.1f} PB"


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
