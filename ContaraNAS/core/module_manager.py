from typing import Any, Dict, Optional
from importlib.metadata import entry_points

from ContaraNAS.core.module import Module


class ModuleManager:
    """Central manager for all system modules"""

    def __init__(self) -> None:
        self.modules: Dict[str, Module] = {}
        self.discover_modules()

    def discover_modules(self):
        try:
            discovered = entry_points(group='contaranas.modules')
            for entry_point in discovered:
                try:
                    module_class = entry_point.load()
                    instance = module_class()
                    self.register(instance)
                    print(f"Loaded module: {entry_point.name}")
                except Exception as e:
                    print(f"Failed to load {entry_point.name}: {e}")
        except Exception as e:
            print(f"No plugins found: {e}")

    def register(self, module: Module):
        """Register a module"""
        self.modules[module.name] = module

    async def enable_module(self, name: str) -> None:
        """Enable a registered module"""
        if name in self.modules:
            await self.modules[name].enable()

    async def disable_module(self, name: str) -> None:
        """Disable a registered module"""
        if name in self.modules:
            await self.modules[name].disable()

    def get_module_state(self, module_name: str) -> Optional[Dict[str, Any]]:
        """Get current state of a specific module"""
        if module_name not in self.modules:
            return None

        module = self.modules[module_name]
        return {
            "name": module_name,
            "enabled": module.enable_flag,
            "initialized": module.init_flag,
            "state": module.state.copy(),
            "tile_data": module.get_tile_data(),
        }

    def get_all_states(self) -> Dict[str, Dict[str, Any]]:
        """Get states of all modules"""
        return {name: self.get_module_state(name) for name in self.modules.keys()}
