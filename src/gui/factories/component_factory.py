from typing import Dict, Type, Callable

from src.core.module import Module
from src.core.utils import get_logger
from src.gui.components.base.module_dialog import ModuleDialog
from src.gui.components.base.module_tile import ModuleTile

logger = get_logger(__name__)


class ComponentFactory:
    """Factory for creating module-specific GUI components"""

    # Type registries
    _tile_classes: Dict[str, Type[ModuleTile]] = {}
    _dialog_classes: Dict[str, Type[ModuleDialog]] = {}

    @classmethod
    def register_components(
            cls,
            module_name: str,
            tile_class: Type[ModuleTile],
            dialog_class: Type[ModuleDialog]
    ) -> None:
        """Register tile and dialog classes for a module type"""
        cls._tile_classes[module_name] = tile_class
        cls._dialog_classes[module_name] = dialog_class
        logger.debug(f"Registered components for module: {module_name}")

    @classmethod
    def create_tile(
            cls,
            name: str,
            module: Module,
            on_enable: Callable,
            on_disable: Callable,
            on_details: Callable
    ) -> ModuleTile:
        """Create appropriate tile for module type"""
        tile_class = cls._tile_classes.get(module.name)
        if not tile_class:
            raise ValueError(f"No tile class registered for module: {module.name}")

        logger.debug(f"Creating tile for module: {name} (type: {module.name})")
        return tile_class(name, module, on_enable, on_disable, on_details)

    @classmethod
    def create_dialog(
            cls,
            name: str,
            module: Module
    ) -> ModuleDialog:
        """Create appropriate dialog for module type"""
        dialog_class = cls._dialog_classes.get(module.name)
        if not dialog_class:
            raise ValueError(f"No dialog class registered for module: {module.name}")

        logger.debug(f"Creating dialog for module: {name} (type: {module.name})")
        return dialog_class(name, module)

    @classmethod
    def get_registered_modules(cls) -> Dict[str, Dict[str, Type]]:
        """Get all registered module types and their component classes"""
        return {
            module_name: {
                'tile_class': cls._tile_classes[module_name],
                'dialog_class': cls._dialog_classes[module_name]
            }
            for module_name in cls._tile_classes.keys()
        }

    @classmethod
    def is_registered(cls, module_name: str) -> bool:
        """Check if a module type has registered components"""
        return module_name in cls._tile_classes and module_name in cls._dialog_classes
