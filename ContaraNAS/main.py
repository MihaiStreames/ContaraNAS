import argparse

import uvicorn

from ContaraNAS.core.utils import get_logger


logger = get_logger(__name__)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="ContaraNAS API Server",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host to bind the server to",
    )

    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind the server to",
    )

    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development",
    )

    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Number of worker processes (only without --reload)",
    )

    parser.add_argument(
        "--log-level",
        type=str,
        default="info",
        choices=["debug", "info", "warning", "error", "critical"],
        help="Logging level",
    )

    return parser.parse_args()


def main():
    """Main entry point"""
    args = parse_args()

    logger.info("Starting ContaraNAS API Server...")
    logger.info(f"Host: {args.host}")
    logger.info(f"Port: {args.port}")
    logger.info(f"Reload: {args.reload}")
    logger.info(f"Workers: {args.workers}")
    logger.info(f"Log Level: {args.log_level}")

    uvicorn_config = {
        "app": "ContaraNAS.api.main:app",
        "host": args.host,
        "port": args.port,
        "log_level": args.log_level,
        "access_log": True,
    }

    if args.reload:
        uvicorn_config["reload"] = True
        uvicorn_config["reload_dirs"] = ["ContaraNAS"]
    else:
        uvicorn_config["workers"] = args.workers

    try:
        uvicorn.run(**uvicorn_config)
    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise


if __name__ == "__main__":
    main()
