from backend.ContaraNAS.core.utils import get_logger
import click


logger = get_logger(__name__)


@click.group()
@click.version_option(version="0.1.0", prog_name="ContaraNAS")
def cli():
    """ContaraNAS - NAS System Monitor & Management"""
    pass


# Import and register command groups
from .module import module_group  # noqa: E402
from .server import server_group  # noqa: E402


cli.add_command(module_group)
cli.add_command(server_group)


def main():
    """Entry point for the CLI"""
    cli()


if __name__ == "__main__":
    main()
