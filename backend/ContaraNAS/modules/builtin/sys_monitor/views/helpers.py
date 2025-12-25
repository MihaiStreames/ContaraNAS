def format_bytes(bytes_value: float) -> str:
    """Format bytes as human readable string"""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if abs(bytes_value) < 1024:
            return f"{bytes_value:.1f} {unit}"

        bytes_value /= 1024

    return f"{bytes_value:.1f} PB"


def format_uptime(seconds: float) -> str:
    """Format uptime in seconds to human readable string"""
    days = int(seconds // 86400)
    hours = int((seconds % 86400) // 3600)
    minutes = int((seconds % 3600) // 60)

    if days > 0:
        return f"{days}d {hours}h {minutes}m"

    if hours > 0:
        return f"{hours}h {minutes}m"

    return f"{minutes}m"


def format_io_time(ms: int) -> str:
    """Format I/O time in milliseconds to human readable string"""
    seconds = ms // 1000
    minutes = seconds // 60
    hours = minutes // 60

    if hours > 0:
        return f"{hours}h {minutes % 60}m"

    if minutes > 0:
        return f"{minutes}m"

    return f"{seconds}s"
