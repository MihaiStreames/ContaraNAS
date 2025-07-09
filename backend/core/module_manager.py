from typing import Dict, Optional, Any

from backend.core.module import Module


class ModuleManager:
    """Central manager for all system modules"""

    def __init__(self) -> None:
        self.modules: Dict[str, Module] = {}

    def register(self, module: Module) -> None:
        """
        Register a module with the manager.
        If a module with the same name already exists, it will be replaced.

        :param module: The Module instance to register
        """
        self.modules[module.name] = module

    async def enable_module(self, name: str) -> None:
        """
        Enable a registered module.
        If the module name doesn't exist, this method does nothing.

        :param name: Name of the module to enable
        :raises Exception: If the module fails to enable
        """
        if name in self.modules:
            await self.modules[name].enable()

    async def disable_module(self, name: str) -> None:
        """
        Disable a registered module.
        If the module name doesn't exist, this method does nothing.

        :param name: Name of the module to disable
        """
        if name in self.modules:
            await self.modules[name].disable()

    def get_dashboard_data(self) -> Dict[str, Dict[str, Any]]:
        """Get dashboard data for all registered modules."""
        return {
            name: {
                "enabled": module.enabled,
                "tile_data": module.get_tile_data(),
                "last_update": module.last_update
            }
            for name, module in self.modules.items()
        }

    def get_module_details(self, name: str) -> Optional[Dict[str, Any]]:
        """Get detailed data for a specific module."""
        if name in self.modules:
            return self.modules[name].get_detailed_data()
        return None
