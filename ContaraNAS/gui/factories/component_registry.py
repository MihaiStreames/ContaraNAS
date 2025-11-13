from ContaraNAS.core.utils import get_logger
from ContaraNAS.gui.components.base.base_tile import BaseTile
from ContaraNAS.gui.factories import ComponentFactory


logger = get_logger(__name__)


def register_all_components() -> None:
    """Register all available GUI components with the factory"""
    logger.info("Registering GUI components...")

    # Register components
    _register_components_from_entry_points()

    registered = ComponentFactory.get_registered_modules()
    logger.info(
        f"Registered components for {len(registered)} module types: {list(registered.keys())}"
    )


def _register_components_from_entry_points() -> None:
    """Register components from entry points defined in pyproject.toml"""
    from importlib.metadata import entry_points

    try:
        discovered = entry_points(group="contaranas.components")
        for entry_point in discovered:
            component_class = entry_point.load()
            assert issubclass(
                component_class, BaseTile
            ), "Component class must have a module_type attribute"
            module_name = entry_point.name
            ComponentFactory.register_components(component_class.module_type, component_class)
            logger.info(f"Registered component for module: {module_name}")
    except Exception as e:
        logger.error(f"Error registering components from entry points: {e}")
