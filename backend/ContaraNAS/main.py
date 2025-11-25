import argparse
import socket

from backend.ContaraNAS.core.utils import get_logger
import uvicorn


logger = get_logger(__name__)


def get_local_ip() -> str:
    """Get the local IP address of this machine"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


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


def print_startup_banner(host: str, port: int) -> None:
    """Print startup banner with connection info"""
    local_ip = get_local_ip()

    print()
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║                                                                ║")
    print("║   ██████╗ ██████╗ ███╗   ██╗████████╗ █████╗ ██████╗  █████╗   ║")
    print("║  ██╔════╝██╔═══██╗████╗  ██║╚══██╔══╝██╔══██╗██╔══██╗██╔══██╗  ║")
    print("║  ██║     ██║   ██║██╔██╗ ██║   ██║   ███████║██████╔╝███████║  ║")
    print("║  ██║     ██║   ██║██║╚██╗██║   ██║   ██╔══██║██╔══██╗██╔══██║  ║")
    print("║  ╚██████╗╚██████╔╝██║ ╚████║   ██║   ██║  ██║██║  ██║██║  ██║  ║")
    print("║   ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝  ║")
    print("║                                                                ║")
    print("╠════════════════════════════════════════════════════════════════╣")
    print("║  NAS System Monitor & Management                               ║")
    print("╠════════════════════════════════════════════════════════════════╣")
    print(f"║  Local:    http://localhost:{port:<5}                              ║")
    print(f"║  Network:  http://{local_ip}:{port:<5}                          ║")
    print("╠════════════════════════════════════════════════════════════════╣")
    print("║  API Docs: /docs                                               ║")
    print("║  Health:   /health                                             ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print()


def main() -> None:
    """Main entry point"""
    args = parse_args()

    logger.info("Starting ContaraNAS API Server...")
    logger.info(f"Host: {args.host}, Port: {args.port}")

    uvicorn_config = {
        "app": "ContaraNAS.api:app",
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

    print_startup_banner(args.host, args.port)

    try:
        uvicorn.run(**uvicorn_config)
    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise


if __name__ == "__main__":
    main()
