"""Helper functions for Steam views"""


def format_bytes(bytes_value: int) -> str:
    """Format bytes as human readable string"""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if abs(bytes_value) < 1024:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024
    return f"{bytes_value:.1f} PB"
