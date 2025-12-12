import socket

import click
import uvicorn

from ContaraNAS.core import get_logger


logger = get_logger(__name__)


def get_local_ip() -> str:
    """Get the local IP address of this machine"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception as e:
        logger.error(f"Error getting local IP address: {e}")
        return "127.0.0.1"


def print_startup_banner(port: int) -> None:
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


@click.command()
@click.option("--host", default="0.0.0.0", show_default=True, help="Host to bind to")
@click.option("--port", default=8000, show_default=True, type=int, help="Port to bind to")
@click.option("--reload", is_flag=True, help="Enable auto-reload for development")
@click.option("--workers", default=1, show_default=True, type=int, help="Number of workers")
@click.option(
    "--log-level",
    type=click.Choice(["debug", "info", "warning", "error"], case_sensitive=False),
    default="info",
    show_default=True,
)
@click.version_option(version="0.1.0", prog_name="ContaraNAS")
def main(host: str, port: int, reload: bool, workers: int, log_level: str):
    """ContaraNAS - NAS System Monitor & Management"""
    logger.info(f"Starting ContaraNAS on {host}:{port}")

    config = {
        "app": "ContaraNAS.api:app",
        "host": host,
        "port": port,
        "log_level": log_level.lower(),
        "access_log": True,
    }

    if reload:
        config["reload"] = True
        config["reload_dirs"] = ["backend/ContaraNAS"]
    else:
        config["workers"] = workers

    print_startup_banner(port)

    try:
        uvicorn.run(**config)
    except KeyboardInterrupt:
        logger.info("Server stopped")


if __name__ == "__main__":
    main()
