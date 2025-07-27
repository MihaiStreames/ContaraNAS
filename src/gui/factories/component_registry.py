from src.core.utils import get_logger

from .component_factory import ComponentFactory

logger = get_logger(__name__)


def register_all_components() -> None:
    """Register all available GUI components with the factory"""
    logger.info("Registering GUI components...")

    # Register components
    _register_steam_components()

    registered = ComponentFactory.get_registered_modules()
    logger.info(
        f"Registered components for {len(registered)} module types: {list(registered.keys())}"
    )


def _register_steam_components() -> None:
    """Register Steam module components"""
    try:
        from src.gui.components.steam.steam_tile import SteamTile

        ComponentFactory.register_components("steam", SteamTile)
        logger.debug("Registered Steam components")

    except ImportError as e:
        logger.warning(f"Failed to register Steam components: {e}")
