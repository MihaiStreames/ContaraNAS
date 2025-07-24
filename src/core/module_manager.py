from typing import Dict, Any

from src.core.module import Module


class ModuleManager:
    """Central manager for all system modules"""

    def __init__(self) -> None:
        self.modules: Dict[str, Module] = {}

    def register(self, module: Module) -> None:
        """Register a module with the manager (if a module with the same name already exists, it will be replaced)"""
        self.modules[module.name] = module

    async def enable_module(self, name: str) -> None:
        """Enable a registered module"""
        if name in self.modules:
            await self.modules[name].enable()

    async def disable_module(self, name: str) -> None:
        """Disable a registered module"""
        if name in self.modules:
            await self.modules[name].disable()

    def get_dashboard_data(self) -> Dict[str, Dict[str, Any]]:
        """Get dashboard data for all registered modules"""
        return {
            name: {
                "enabled": module.enable_flag,
                "tile_data": module.get_tile_data(),
            }
            for name, module in self.modules.items()
        }
