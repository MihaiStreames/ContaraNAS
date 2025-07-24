from typing import Dict, Type, Callable

from src.core.module import Module
from src.core.utils import get_logger
from src.gui.components.base.module_tile import ModuleTile

logger = get_logger(__name__)


class ComponentFactory:
    """Factory for creating module-specific GUI components"""

    # Type registries
    _tile_classes: Dict[str, Type[ModuleTile]] = {}

    @classmethod
    def register_components(cls, module_name: str, tile_class: Type[ModuleTile]) -> None:
        """Register tile and dialog classes for a module type"""
        cls._tile_classes[module_name] = tile_class
        logger.debug(f"Registered components for module: {module_name}")

    @classmethod
    def create_tile(cls, name: str, module: Module, on_enable: Callable, on_disable: Callable) -> ModuleTile:
        """Create appropriate tile for module type"""
        tile_class = cls._tile_classes.get(module.name)
        if not tile_class:
            raise ValueError(f"No tile class registered for module: {module.name}")

        logger.debug(f"Creating tile for module: {name} (type: {module.name})")
        return tile_class(name, module, on_enable, on_disable)

    @classmethod
    def get_registered_modules(cls) -> Dict[str, Dict[str, Type]]:
        """Get all registered module types and their component classes"""
        return {
            module_name: {'tile_class': cls._tile_classes[module_name]}
            for module_name in cls._tile_classes.keys()
        }

    @classmethod
    def is_registered(cls, module_name: str) -> bool:
        """Check if a module type has registered components"""
        return module_name in cls._tile_classes
