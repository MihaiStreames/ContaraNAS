from backend.core.module import Module


class ModuleManager:
    def __init__(self):
        self.modules = {}

    def register(self, module: Module):
        """Register a module"""
        self.modules[module.name] = module

    async def enable_module(self, name: str):
        """Enable a module"""
        if name in self.modules:
            await self.modules[name].enable()

    async def disable_module(self, name: str):
        """Disable a module"""
        if name in self.modules:
            await self.modules[name].disable()

    def get_dashboard_data(self):
        """Get data for all modules"""
        return {
            name: {
                "enabled": module.enabled,
                "tile_data": module.get_tile_data(),
                "last_update": module.last_update
            }
            for name, module in self.modules.items()
        }

    def get_module_details(self, name: str):
        """Get detailed data for a specific module"""
        if name in self.modules:
            return self.modules[name].get_detailed_data()
        return None
