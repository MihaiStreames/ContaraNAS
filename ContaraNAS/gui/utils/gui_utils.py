def format_bytes(bytes_size: int) -> str:
    """Format bytes into human readable format"""
    size: float = float(bytes_size)
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} PB"
