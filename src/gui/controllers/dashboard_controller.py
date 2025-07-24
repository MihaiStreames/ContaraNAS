from nicegui import ui

from src.core.module_manager import ModuleManager


class DashboardController:
    """Handles commands from GUI components"""

    def __init__(self, module_manager: ModuleManager):
        self.module_manager = module_manager

    async def enable_module(self, module_name: str):
        """Handle enable command"""
        try:
            await self.module_manager.enable_module(module_name)
            ui.notify(f"Module '{module_name}' enabled successfully", type='positive')
        except Exception as e:
            ui.notify(f"Failed to enable '{module_name}': {str(e)}", type='negative')

    async def disable_module(self, module_name: str):
        """Handle disable command"""
        try:
            await self.module_manager.disable_module(module_name)
            ui.notify(f"Module '{module_name}' disabled successfully", type='warning')
        except Exception as e:
            ui.notify(f"Failed to disable '{module_name}': {str(e)}", type='negative')
