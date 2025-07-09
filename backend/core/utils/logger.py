import logging
import os


def get_logger(name: str) -> logging.Logger:
    """Create and configure a logger with both file and console handlers."""
    print(f"get_logger called for: {name}")
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Prevent duplicate handlers
    if not logger.hasHandlers():
        # Create log file in the same directory as this module
        log_dir = os.path.dirname(os.path.abspath(__file__))
        log_file = os.path.join(log_dir, "app.log")

        # Persistent logging
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)

        # Real-time monitoring
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)

        # Consistent formatting for both handlers
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] %(name)s: %(message)s"
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger
