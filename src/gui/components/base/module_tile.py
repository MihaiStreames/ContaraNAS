from abc import ABC, abstractmethod
from typing import Callable

from nicegui import ui

from src.core.module import Module
from src.core.utils import get_logger

logger = get_logger(__name__)


class ModuleTile(ABC):
    """Abstract base class for module tiles"""

    def __init__(self, name: str, module: Module, on_enable: Callable, on_disable: Callable):
        self.name = name
        self.module = module
        self.on_enable = on_enable
        self.on_disable = on_disable

        # UI elements that need updating
        self.status_badge = None
        self.enable_button = None
        self.disable_button = None
        self.info_container = None

        self._create_tile()

    def update_state(self, event_data=None):
        """Update the tile's state to reflect current module status"""
        self.status_badge.set_text(self._get_status_text())
        self.status_badge.props(f'color={self._get_status_color()}')

        self._update_info()
        self._update_buttons()

    @abstractmethod
    def render(self, tile_data: dict):
        """Render module-specific data in the tile"""
        pass

    def _create_tile(self):
        """Create the tile UI"""
        with ui.card().classes('w-72 min-h-[180px] p-4'):
            # Header with name and status
            with ui.row().classes('w-full items-center justify-between mb-4'):
                ui.label(self.name.title()).classes('text-lg font-bold')

                self.status_badge = ui.badge(
                    self._get_status_text(),
                    color=self._get_status_color()
                )

            # Info container
            self.info_container = ui.column().classes('w-full mb-4 flex-1')
            self._update_info()

            # Action buttons
            with ui.row().classes('w-full justify-end gap-2'):
                self.enable_button = ui.button(
                    "Enable",
                    icon="play_arrow",
                    on_click=lambda: self.on_enable(self.name)
                ).props('size=sm color=positive')

                self.disable_button = ui.button(
                    "Disable",
                    icon="stop",
                    on_click=lambda: self.on_disable(self.name)
                ).props('size=sm color=warning')

            self._update_buttons()

    def _get_status_text(self) -> str:
        """Get the status text for the module"""
        return "Running" if self.module.enable_flag else "Stopped"

    def _get_status_color(self) -> str:
        """Get the status color for the module"""
        return "positive" if self.module.enable_flag else "grey"

    def _update_buttons(self):
        """Update the enable/disable button states"""
        if self.module.enable_flag:
            self.enable_button.set_visibility(False)
            self.disable_button.set_visibility(True)
        else:
            self.enable_button.set_visibility(True)
            self.disable_button.set_visibility(False)

    def _update_info(self):
        """Update the display in the tile"""
        self.info_container.clear()

        try:
            tile_data = self.module.get_tile_data()

            with self.info_container:
                # Show module-specific basic stats
                self.render(tile_data)

        except Exception as e:
            logger.error(f"Error updating info for {self.name}: {e}")
            with self.info_container:
                ui.label("Error loading info").classes('text-red-500 text-sm')
