from typing import Any

from nicegui import ui

from ContaraNAS.core.event_bus import event_bus
from ContaraNAS.core.utils import get_logger
from ContaraNAS.gui.components.base import BaseTile
from ContaraNAS.gui.components.base.base_view_model import BaseTileViewModel
from ContaraNAS.gui.components.sys_monitor import sys_monitor_tile_helper as helper
from ContaraNAS.modules.sys_monitor.constants import MAX_HISTORY_POINTS
from ContaraNAS.modules.sys_monitor.controllers import SysMonitorController
from ContaraNAS.modules.sys_monitor.services import SysMonitorPreferenceService


logger = get_logger(__name__)


class SysMonitorTile(BaseTile):
    """System Monitor-specific module tile implementation"""

    module_type = "sys_monitor"

    def __init__(self, view_model: BaseTileViewModel, controller: SysMonitorController):
        self._cpu_core_history: dict[int, list[float]] = {}
        self._cpu_general_history: list[float] = []
        self._mem_history: list[float] = []
        self._max_history_points: int = MAX_HISTORY_POINTS

        # Initialize preference service and load user preference for CPU view
        self.preference_service: SysMonitorPreferenceService = SysMonitorPreferenceService()
        self._show_per_core: bool = self.preference_service.get_cpu_view_preference()

        # Tab references
        self._cpu_tab_ref: Any = None
        self._ram_tab_ref: Any = None
        self._disks_tab_ref: Any = None
        self._tabs_ref: Any = None

        # UI element references
        self._tabs_init_flag: bool = False
        self._cpu_tab_panel: Any = None
        self._ram_tab_panel: Any = None
        self._disks_tab_panel: Any = None

        super().__init__(view_model, controller)

    def _create_tile(self):
        """Create the tile UI with double width"""
        with ui.card().classes("w-[576px] min-h-[180px] p-4"):
            # Header
            with ui.row().classes("w-full items-center justify-between mb-4"):
                ui.label(self.view_model.display_name).classes("text-lg font-bold")

                self.status_badge = ui.badge(
                    self.view_model.status_text, color=self.view_model.status_color
                )

            # Info container
            self.info_container = ui.column().classes("w-full mb-4 flex-1")

            # Buttons
            with ui.row().classes("w-full justify-end gap-2"):
                self.enable_button = ui.button(
                    "Enable",
                    icon="play_arrow",
                    on_click=lambda: self.controller.enable_module(self.view_model.name),
                ).props("size=sm color=positive")

                self.disable_button = ui.button(
                    "Disable",
                    icon="stop",
                    on_click=lambda: self.controller.disable_module(self.view_model.name),
                ).props("size=sm color=warning")

            self._refresh_ui()

    def _setup_event_listeners(self):
        """Listen for state changes"""
        event_bus.subscribe(
            f"module.{self.view_model.name}.state_changed", self._handle_state_change
        )

    def _handle_state_change(self, event_data):
        """Update view model and refresh UI while preserving tab state"""
        self.view_model = BaseTileViewModel.from_module_state(self.view_model.name, event_data)
        self._refresh_ui()

    def _update_info(self):
        """Update the info container with current data while preserving tab selection"""
        if not self._tabs_init_flag:
            # First time: create the tabs structure
            self.info_container.clear()
            with self.info_container:
                self._initialize_tabs(self.view_model.tile_data)
            self._tabs_init_flag = True
        else:
            # Subsequent updates: just update the values without clearing
            self._update_tab_contents(self.view_model.tile_data)

    def _toggle_cpu_view(self):
        """Toggle between per-core and general CPU view"""
        self._show_per_core = not self._show_per_core
        self.preference_service.set_cpu_view_preference(self._show_per_core)

        # Force a refresh by re-initializing tabs
        self._tabs_init_flag = False
        self._update_info()

    def _initialize_tabs(self, tile_data: dict):
        """Initialize the tab structure"""
        if not tile_data:
            ui.label("No system data available").classes("text-sm text-gray-500")
            return

        cpu = tile_data.get("cpu")
        memory = tile_data.get("memory")
        disks = tile_data.get("disks", [])

        logger.debug(f"Initializing tabs - CPU: {cpu is not None}, Memory: {memory is not None}, Disks: {len(disks) if disks else 0}")

        # Create tabs for CPU, RAM, and Disks
        with ui.tabs().classes('w-full') as tabs:
            self._cpu_tab_ref = ui.tab('CPU')
            self._ram_tab_ref = ui.tab('RAM')
            self._disks_tab_ref = ui.tab('Disks')

        # Store tabs reference
        self._tabs_ref = tabs

        with ui.tab_panels(tabs, value=self._cpu_tab_ref).classes('w-full'):
            # CPU Tab
            with ui.tab_panel(self._cpu_tab_ref) as cpu_panel:
                self._cpu_tab_panel = cpu_panel
                if cpu:
                    self._render_cpu_tab(cpu)
                else:
                    ui.label("No CPU data available").classes("text-sm text-gray-500")

            # RAM Tab
            with ui.tab_panel(self._ram_tab_ref) as ram_panel:
                self._ram_tab_panel = ram_panel
                if memory:
                    self._render_ram_tab(memory)
                else:
                    ui.label("No memory data available").classes("text-sm text-gray-500")

            # Disks Tab
            with ui.tab_panel(self._disks_tab_ref) as disks_panel:
                self._disks_tab_panel = disks_panel
                if disks:
                    self._render_disks_tab(disks)
                else:
                    ui.label("No disk data available").classes("text-sm text-gray-500")

    def _update_tab_contents(self, tile_data: dict):
        """Update only the values in existing tabs without recreating them"""
        if not tile_data:
            return

        cpu = tile_data.get("cpu")
        memory = tile_data.get("memory")
        disks = tile_data.get("disks", [])

        # Update CPU tab
        if cpu and self._cpu_tab_panel:
            self._cpu_tab_panel.clear()
            with self._cpu_tab_panel:
                self._render_cpu_tab(cpu)

        # Update RAM tab
        if memory and self._ram_tab_panel:
            self._ram_tab_panel.clear()
            with self._ram_tab_panel:
                self._render_ram_tab(memory)

        # Update Disks tab
        if disks and self._disks_tab_panel:
            self._disks_tab_panel.clear()
            with self._disks_tab_panel:
                self._render_disks_tab(disks)

    def render(self, tile_data: dict):
        """Render System Monitor-specific stats in the tile with tabs (for base class compatibility)"""
        self._initialize_tabs(tile_data)

    def _render_cpu_tab(self, cpu):
        """Render CPU information"""
        self._cpu_core_history, self._cpu_general_history = helper.render_cpu_tab(
            cpu,
            self._show_per_core,
            self._cpu_core_history,
            self._cpu_general_history,
            self._max_history_points,
            self._toggle_cpu_view
        )

    def _render_ram_tab(self, memory):
        """Render RAM information"""
        self._mem_history = helper.render_ram_tab(
            memory,
            self._mem_history,
            self._max_history_points
        )

    def _render_disks_tab(self, disks):
        """Render disk information"""
        helper.render_disks_tab(disks)
