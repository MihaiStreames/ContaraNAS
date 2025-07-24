from typing import Dict, Type

from src.core.utils import get_logger
from src.gui.components.base.base_tile import BaseTile
from src.gui.components.base.base_view_model import BaseTileViewModel

logger = get_logger(__name__)


class ComponentFactory:
    """Factory for creating module-specific GUI components"""

    # Type registries
    _tile_classes: Dict[str, Type[BaseTile]] = {}

    @classmethod
    def register_components(cls, module_name: str, tile_class: Type[BaseTile]) -> None:
        """Register tile and dialog classes for a module type"""
        cls._tile_classes[module_name] = tile_class
        logger.debug(f"Registered components for module: {module_name}")

    @classmethod
    def create_tile(cls, view_model: BaseTileViewModel, controller) -> BaseTile:
        """Create tile from ViewModel"""
        tile_class = cls._tile_classes.get(view_model.name, BaseTile)
        return tile_class(view_model, controller)

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
