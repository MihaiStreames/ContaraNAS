from abc import ABC, abstractmethod
from typing import Callable

from nicegui import ui

from src.core.module import Module
from src.core.utils import get_logger

logger = get_logger(__name__)


class ModuleTile(ABC):
    """Abstract base class for module tiles"""

    def __init__(
            self,
            name: str,
            module: Module,
            on_enable: Callable,
            on_disable: Callable,
            on_details: Callable
    ):
        self.name = name
        self.module = module
        self.on_enable = on_enable
        self.on_disable = on_disable
        self.on_details = on_details

        # UI elements that need updating
        self.status_badge = None
        self.enable_button = None
        self.disable_button = None
        self.stats_container = None

        self._create_tile()

    def update_state(self):
        """Update the tile's state to reflect current module status"""
        try:
            # Update status badge
            self.status_badge.set_text(self._get_status_text())
            self.status_badge.props(f'color={self._get_status_color()}')

            # Update stats
            self._update_stats()

            # Update button states
            self._update_buttons()

        except Exception as e:
            logger.error(f"Error updating tile for {self.name}: {e}")

    def _create_tile(self):
        """Create the tile UI"""
        with ui.card().classes('w-80 min-h-[200px] p-4'):
            # Header with name and status
            with ui.row().classes('w-full items-center justify-between mb-2'):
                ui.label(self.name.title()).classes('text-lg font-bold')
                self.status_badge = ui.badge(
                    self._get_status_text(),
                    color=self._get_status_color()
                )

            # Module stats container
            self.stats_container = ui.column().classes('w-full mb-4')
            self._update_stats()

            # Action buttons
            with ui.row().classes('w-full justify-end gap-2'):
                self.enable_button = ui.button(
                    "Enable",
                    icon="play_arrow",
                    on_click=lambda: self.on_enable(self.name)
                ).props('size=sm')

                self.disable_button = ui.button(
                    "Disable",
                    icon="stop",
                    on_click=lambda: self.on_disable(self.name)
                ).props('size=sm color=warning')

                ui.button(
                    "Details",
                    icon="info",
                    on_click=lambda: self.on_details(self.name)
                ).props('size=sm flat')

            # Update button states
            self._update_buttons()

    def _get_status_text(self) -> str:
        """Get the status text for the module."""
        if self.module.enabled:
            return "Running"
        return "Stopped"

    def _get_status_color(self) -> str:
        """Get the status color for the module."""
        if self.module.enabled:
            return "positive"
        return "grey"

    def _update_buttons(self):
        """Update the enable/disable button states"""
        if self.module.enabled:
            self.enable_button.set_visibility(False)
            self.disable_button.set_visibility(True)
        else:
            self.enable_button.set_visibility(True)
            self.disable_button.set_visibility(False)

    def _update_stats(self):
        """Update the display in the tile"""
        self.stats_container.clear()

        try:
            tile_data = self.module.get_tile_data()

            with self.stats_container:
                self._render_stats(tile_data)

        except Exception as e:
            logger.error(f"Error updating stats for {self.name}: {e}")
            with self.stats_container:
                ui.label("Error loading stats").classes('text-red-500')

    @abstractmethod
    def _render_stats(self, tile_data: dict):
        """Render module-specific stats in the tile. Must be implemented by subclasses"""
        pass
