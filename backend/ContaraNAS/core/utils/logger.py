import sys

from backend.ContaraNAS.core import settings
import loguru
from loguru import logger


def setup_logging(
    level: str = "DEBUG",
    rotation: str = "10 MB",
    retention: str = "1 week",
    compression: str = "zip",
) -> None:
    """Call once at startup"""
    log_dir = settings.log_dir
    log_dir.mkdir(parents=True, exist_ok=True)

    # Remove default handler
    logger.remove()

    # Console handler - INFO and above, colored
    logger.add(
        sys.stderr,
        level="INFO",
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        ),
        colorize=True,
    )

    # File handler - DEBUG and above, with rotation
    logger.add(
        log_dir / "contaranas.log",
        level=level,
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}",
        rotation=rotation,
        retention=retention,
        compression=compression,
        encoding="utf-8",
        enqueue=True,
    )

    # Separate error log for easier debugging
    logger.add(
        log_dir / "errors.log",
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}\n{exception}",
        rotation="5 MB",
        retention="1 month",
        compression=compression,
        encoding="utf-8",
        enqueue=True,
        backtrace=True,
        diagnose=True,
    )

    logger.info("Logging initialized", log_dir=str(log_dir))


def get_logger(name: str) -> loguru.Logger:
    return logger.bind(name=name)
