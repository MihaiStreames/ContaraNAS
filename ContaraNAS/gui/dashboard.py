from nicegui import ui

from ContaraNAS.core.module_manager import ModuleManager
from ContaraNAS.core.utils import get_logger
from ContaraNAS.gui.components.base import BaseTile, BaseTileViewModel
from ContaraNAS.gui.controllers import DashboardController
from ContaraNAS.gui.factories import ComponentFactory


logger = get_logger(__name__)


class DashboardView:
    """Main dashboard view for managing modules"""

    def __init__(self, module_manager: ModuleManager):
        self.module_manager = module_manager
        self.controller = DashboardController(module_manager)
        self.tiles: dict[str, BaseTile] = {}
        self._setup_ui()

    def _setup_ui(self):
        """Setup dashboard UI"""
        with ui.header():
            ui.label("ContaraNAS").classes("text-h4 font-bold")

        with ui.column().classes("p-4 w-full"):
            ui.label("Modules").classes("text-h5 mb-4")

            self.tiles_container = ui.row().classes("gap-4 w-full")
            self._create_tiles()

    def _create_tiles(self):
        """Create tiles from current module states"""
        module_states = self.module_manager.get_all_states()

        with self.tiles_container:
            for name, state in module_states.items():
                view_model = BaseTileViewModel.from_module_state(name, state)
                tile = ComponentFactory.create_tile(view_model, self.controller)
                if tile is not None:
                    self.tiles[name] = tile
