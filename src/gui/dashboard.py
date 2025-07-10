from typing import Dict

from nicegui import ui

from src.core.module_manager import ModuleManager
from src.core.utils import get_logger
from src.gui.components.base.module_detail_dialog import ModuleDetailDialog
from src.gui.components.base.module_tile import ModuleTile

logger = get_logger(__name__)


class DashboardView:
    """Main dashboard view for managing modules"""

    def __init__(self, module_manager: ModuleManager):
        self.manager = module_manager
        self.tiles: Dict[str, ModuleTile] = {}

        self._setup_ui()

    def _setup_ui(self):
        """Setup the main dashboard UI"""
        logger.info("Setting up dashboard UI...")

        with ui.header():
            ui.label("NAS Manager").classes('text-h4 font-bold')

        with ui.column().classes('p-4 w-full'):
            ui.label("Modules").classes('text-h5 mb-4')

            self.tiles_container = ui.row().classes('gap-4 w-full')
            self._create_module_tiles()

    def _create_module_tiles(self):
        """Create tiles for all registered modules"""
        logger.debug("Creating module tiles...")

        with self.tiles_container:
            for name, module in self.manager.modules.items():
                tile = ModuleTile(
                    name=name,
                    module=module,
                    on_enable=self._enable_module,
                    on_disable=self._disable_module,
                    on_details=self._show_module_details
                )
                self.tiles[name] = tile

        logger.debug(f"Created {len(self.tiles)} module tiles")

    async def _enable_module(self, name: str):
        """Enable a module"""
        logger.info(f"Enabling module: {name}")

        try:
            await self.manager.enable_module(name)
            ui.notify(f"Module '{name}' enabled successfully", type='positive')

            # Update the specific tile
            if name in self.tiles:
                self.tiles[name].update_state()

        except Exception as e:
            logger.error(f"Failed to enable module {name}: {e}")
            ui.notify(f"Failed to enable '{name}': {str(e)}", type='negative')

    async def _disable_module(self, name: str):
        """Disable a module"""
        logger.info(f"Disabling module: {name}")

        try:
            await self.manager.disable_module(name)
            ui.notify(f"Module '{name}' disabled successfully", type='warning')

            # Update the specific tile
            if name in self.tiles:
                self.tiles[name].update_state()

        except Exception as e:
            logger.error(f"Failed to disable module {name}: {e}")
            ui.notify(f"Failed to disable '{name}': {str(e)}", type='negative')

    def _show_module_details(self, name: str):
        """Show detailed information about a module"""
        logger.debug(f"Showing details for module: {name}")

        if name in self.manager.modules:
            module = self.manager.modules[name]
            ModuleDetailDialog(name, module)
        else:
            ui.notify(f"Module '{name}' not found", type='negative')