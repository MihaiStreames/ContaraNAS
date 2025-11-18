from typing import Any

from nicegui import ui

from ContaraNAS.core.exceptions import ModuleError, ModuleInitializationError
from ContaraNAS.core.module_manager import ModuleManager


class DashboardController:
    """Handles commands from GUI components"""

    def __init__(self, module_manager: ModuleManager):
        self._module_manager = module_manager

    async def enable_module(self, module_name: str):
        """Handle enable command"""
        try:
            await self._module_manager.enable_module(module_name)
            ui.notify(f"Module '{module_name}' enabled successfully", type="positive")
        except ModuleInitializationError as e:
            ui.notify(f"Failed to start {module_name}: {e.reason}", type="negative")

    async def disable_module(self, module_name: str):
        """Handle disable command"""
        try:
            await self._module_manager.disable_module(module_name)
            ui.notify(f"Module '{module_name}' disabled successfully", type="warning")
        except ModuleError as e:
            ui.notify(f"Failed to stop {module_name}: {e.reason}", type="negative")

    def get_module_controller(self, module_name: str) -> Any:
        """Get the controller for a specific module"""
        if module_name in self._module_manager.modules:
            module = self._module_manager.modules[module_name]
            return module.controller
        return None
