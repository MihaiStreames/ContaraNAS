def format_bytes(bytes_size: int | float, precision: int = 1) -> str:
    """Format bytes into human readable format"""
    size: float = float(bytes_size)
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024.0:
            return f"{size:.{precision}f} {unit}"
        size /= 1024.0
    return f"{size:.{precision}f} PB"


def format_speed(bytes_per_second: float, precision: int = 1) -> str:
    """Format bytes/second into human readable speed"""
    return f"{format_bytes(bytes_per_second, precision)}/s"


def format_duration(seconds: float, style: str = "colon") -> str:
    """Format duration in seconds to human readable string"""
    days = int(seconds // 86400)
    hours = int((seconds % 86400) // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    if style == "colon":
        return f"{days:02d}:{hours:02d}:{minutes:02d}:{secs:02d}"

    # Human readable style
    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if secs > 0 or not parts:
        parts.append(f"{secs}s")

    return " ".join(parts)


def format_percentage(value: float, precision: int = 1) -> str:
    """Format a percentage value"""
    return f"{value:.{precision}f}%"


def format_frequency(ghz: float, precision: int = 2) -> str:
    """Format CPU frequency in GHz"""
    return f"{ghz:.{precision}f} GHz"
