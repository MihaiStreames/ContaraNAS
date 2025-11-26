from backend.ContaraNAS.cli.installer import ModuleInstaller
from backend.ContaraNAS.core.utils import get_logger
import click


logger = get_logger(__name__)


@click.group(name="module")
def module_group():
    """Manage ContaraNAS modules"""
    pass


@module_group.command(name="install")
@click.argument("path", type=click.Path(exists=True, dir_okay=False, resolve_path=True))
def install(path: str):
    """Install a module from a .zip file

    \b
    Examples:
        contaranas module install my-module.zip
        contaranas module install /path/to/module.zip
    """
    installer = ModuleInstaller()
    success = installer.install(path)
    raise SystemExit(0 if success else 1)


@module_group.command(name="uninstall")
@click.argument("name")
@click.confirmation_option(prompt="Are you sure you want to uninstall this module?")
def uninstall(name: str):
    """Uninstall a community module

    \b
    Examples:
        contaranas module uninstall my-module
    """
    installer = ModuleInstaller()
    success = installer.uninstall(name)
    raise SystemExit(0 if success else 1)


@module_group.command(name="list")
@click.option(
    "--source",
    type=click.Choice(["all", "builtin", "community"], case_sensitive=False),
    default="all",
    help="Filter modules by source",
)
def list_modules(source: str):
    """List all installed modules

    \b
    Examples:
        contaranas module list
        contaranas module list --source builtin
        contaranas module list --source community
    """
    installer = ModuleInstaller()
    installer.list_modules(source_filter=source)
