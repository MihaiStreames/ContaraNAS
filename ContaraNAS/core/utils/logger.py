import logging
import platform
from pathlib import Path


def get_log_dir() -> Path:
    """Get the appropriate log directory for the platform"""
    system = platform.system()

    if system == "Linux":
        return Path.home() / ".local" / "share" / "contaranas" / "logs"
    elif system == "Windows":
        return Path.home() / "AppData" / "Local" / "contaranas" / "logs"
    else:
        # Unknown platform, fallback to home directory
        return Path.home() / ".contaranas" / "logs"


def get_logger(name: str) -> logging.Logger:
    """Create and configure a logger with a file handler"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Prevent duplicate handlers
    if not logger.hasHandlers():
        log_dir = get_log_dir()
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / "app.log"

        # Persistent logging
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)

        # Consistent formatting
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] %(name)s: %(message)s"
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        logger.propagate = False

    return logger
