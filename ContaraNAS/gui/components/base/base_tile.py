from abc import ABC, abstractmethod
from typing import Any

from nicegui import ui

from ContaraNAS.core.event_bus import event_bus
from ContaraNAS.core.utils import get_logger

from .base_view_model import BaseTileViewModel


logger = get_logger(__name__)


class BaseTile(ABC):
    """Abstract base class for module tiles"""

    module_type: str = "base"

    def __init__(self, view_model: BaseTileViewModel, controller: Any):
        self.view_model: BaseTileViewModel = view_model
        self.controller: Any = controller

        # UI elements (initialized in _create_tile)
        self._status_badge: Any = None
        self._enable_button: Any = None
        self._disable_button: Any = None
        self._info_container: Any = None
        self._create_tile()
        self._setup_event_listeners()

    @abstractmethod
    def render(self, tile_data: dict):
        """Render module-specific data in the tile"""

    def _setup_event_listeners(self):
        """Listen for state changes"""
        event_bus.subscribe(
            f"module.{self.view_model.name}.state_changed", self._handle_state_change
        )

    def _handle_state_change(self, event_data):
        """Update view model and refresh UI"""
        self.view_model = BaseTileViewModel.from_module_state(self.view_model.name, event_data)
        self._refresh_ui()

    def _create_tile(self):
        """Create the tile UI"""
        with ui.card().classes("w-72 min-h-[180px] p-4"):
            # Header
            with ui.row().classes("w-full items-center justify-between mb-4"):
                ui.label(self.view_model.display_name).classes("text-lg font-bold")

                self._status_badge = ui.badge(
                    self.view_model.status_text, color=self.view_model.status_color
                )

            # Info container
            self._info_container = ui.column().classes("w-full mb-4 flex-1")

            # Buttons
            with ui.row().classes("w-full justify-end gap-2"):
                self._enable_button = ui.button(
                    "Enable",
                    icon="play_arrow",
                    on_click=lambda: self.controller.enable_module(self.view_model.name),
                ).props("size=sm color=positive")

                self._disable_button = ui.button(
                    "Disable",
                    icon="stop",
                    on_click=lambda: self.controller.disable_module(self.view_model.name),
                ).props("size=sm color=warning")

            self._refresh_ui()

    def _refresh_ui(self):
        """Update UI to match current view model"""
        # Update status badge
        self._status_badge.set_text(self.view_model.status_text)
        self._status_badge.props(f"color={self.view_model.status_color}")

        # Update buttons
        if self.view_model.enabled:
            self._enable_button.set_visibility(False)
            self._disable_button.set_visibility(True)
        else:
            self._enable_button.set_visibility(True)
            self._disable_button.set_visibility(False)

        # Update info display
        self._update_info()

    def _update_info(self):
        """Update the info container with current data"""
        self._info_container.clear()

        with self._info_container:
            self.render(self.view_model.tile_data)
