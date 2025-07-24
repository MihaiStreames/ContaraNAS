from datetime import datetime
from typing import Union


def format_bytes(bytes_size: int) -> str:
    """Format bytes into human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} PB"


def format_relative_time(timestamp: Union[datetime, str, None]) -> str:
    """Format timestamp as relative time (e.g., '5m ago', 'Just now')"""
    if not timestamp:
        return "Never"

    # Handle string timestamps
    if isinstance(timestamp, str):
        try:
            timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        except ValueError:
            return "Invalid time"

    # Ensure timezone-naive datetime for comparison
    if timestamp.tzinfo is not None:
        timestamp = timestamp.replace(tzinfo=None)

    time_diff = datetime.now() - timestamp
    total_seconds = time_diff.total_seconds()

    if total_seconds < 60:
        return "Just now"
    elif total_seconds < 3600:
        minutes = int(total_seconds / 60)
        return f"{minutes}m ago"
    elif total_seconds < 86400:
        hours = int(total_seconds / 3600)
        return f"{hours}h ago"
    else:
        days = int(total_seconds / 86400)
        return f"{days}d ago"
