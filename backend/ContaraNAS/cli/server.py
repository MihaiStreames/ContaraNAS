import socket

from backend.ContaraNAS.core.utils import get_logger
import click
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


@click.group(name="server")
def server_group():
    """Server management commands"""
    pass


@server_group.command(name="start")
@click.option("--host", default="0.0.0.0", show_default=True, help="Host to bind the server to")
@click.option(
    "--port", default=8000, show_default=True, type=int, help="Port to bind the server to"
)
@click.option("--reload", is_flag=True, help="Enable auto-reload for development")
@click.option(
    "--workers",
    default=1,
    show_default=True,
    type=int,
    help="Number of worker processes (ignored with --reload)",
)
@click.option(
    "--log-level",
    type=click.Choice(["debug", "info", "warning", "error", "critical"], case_sensitive=False),
    default="info",
    show_default=True,
    help="Logging level",
)
def start(host: str, port: int, reload: bool, workers: int, log_level: str):
    """Start the ContaraNAS API server

    \b
    Examples:
        contaranas server start
        contaranas server start --reload
        contaranas server start --host 0.0.0.0 --port 8080
        contaranas server start --workers 4 --log-level debug
    """
    logger.info("Starting ContaraNAS API Server...")
    logger.info(f"Host: {host}, Port: {port}")

    uvicorn_config = {
        "app": "ContaraNAS.api:app",
        "host": host,
        "port": port,
        "log_level": log_level.lower(),
        "access_log": True,
    }

    if reload:
        uvicorn_config["reload"] = True
        uvicorn_config["reload_dirs"] = ["ContaraNAS"]
    else:
        uvicorn_config["workers"] = workers

    print_startup_banner(port)

    try:
        uvicorn.run(**uvicorn_config)
    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise
