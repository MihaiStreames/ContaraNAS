from nicegui import ui

from ContaraNAS.core.event_bus import event_bus
from ContaraNAS.core.utils import get_logger
from ContaraNAS.gui.components.base import BaseTile
from ContaraNAS.gui.components.base.base_view_model import BaseTileViewModel
from ContaraNAS.gui.components.sys_monitor.sub_components import (
    CPUStatsComponent,
    DiskStatsComponent,
    MemoryStatsComponent,
)
from ContaraNAS.modules.sys_monitor.constants import (
    MAX_HISTORY_POINTS,
)
from ContaraNAS.modules.sys_monitor.controllers import SysMonitorController
from ContaraNAS.modules.sys_monitor.services import SysMonitorPreferenceService


logger = get_logger(__name__)


class SysMonitorTile(BaseTile):
    """System Monitor tile using shared component patterns"""

    module_type = "sys_monitor"

    def __init__(self, view_model: BaseTileViewModel, controller: SysMonitorController):
        # Preference service for persistent settings
        self._preference_service = SysMonitorPreferenceService()
        self._show_per_core: bool = self._preference_service.get_cpu_view_preference()

        # Sub-components
        self._cpu_component = CPUStatsComponent(max_history=MAX_HISTORY_POINTS)
        self._memory_component = MemoryStatsComponent(max_history=MAX_HISTORY_POINTS)
        self._disk_component = DiskStatsComponent()

        # Tab state
        self._tabs_initialized: bool = False
        self._tab_panels: dict[str, ui.tab_panel] = {}
        self._tab_refs: dict[str, ui.tab] = {}

        super().__init__(view_model, controller)

    def _create_tile(self) -> None:
        """Create double-width tile layout"""
        with ui.card().classes("w-[576px] min-h-[180px] p-4"):
            # Header
            with ui.row().classes("w-full items-center justify-between mb-4"):
                ui.label(self.view_model.display_name).classes("text-lg font-bold")
                self._status_badge = ui.badge(
                    self.view_model.status_text, color=self.view_model.status_color
                )

            # Content container
            self._info_container = ui.column().classes("w-full mb-4 flex-1")

            # Control buttons
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

    def _setup_event_listeners(self) -> None:
        """Subscribe to module state changes"""
        event_bus.subscribe(
            f"module.{self.view_model.name}.state_changed",
            self._handle_state_change,
        )

    def _handle_state_change(self, event_data: dict) -> None:
        """Handle state updates"""
        self.view_model = BaseTileViewModel.from_module_state(self.view_model.name, event_data)
        self._refresh_ui()

    def _update_info(self) -> None:
        """Update content"""
        tile_data = self.view_model.tile_data

        if not self._tabs_initialized:
            # First render - create full tab structure
            self._info_container.clear()
            with self._info_container:
                self._create_tabs(tile_data)
            self._tabs_initialized = True
        else:
            # Subsequent updates - only refresh tab contents
            self._update_tab_contents(tile_data)

    def render(self, tile_data: dict) -> None:
        """Base class compatibility delegated to _create_tabs"""
        self._create_tabs(tile_data)

    # -------------------------------------------------------------------------
    # Tab Management
    # -------------------------------------------------------------------------

    def _create_tabs(self, tile_data: dict) -> None:
        """Create tabbed interface structure"""
        if not tile_data:
            ui.label("No system data available").classes("text-sm text-gray-500")
            return

        cpu = tile_data.get("cpu")
        memory = tile_data.get("memory")
        disks = tile_data.get("disks", [])

        # Create tabs
        with ui.tabs().classes("w-full") as tabs:
            self._tab_refs["cpu"] = ui.tab("CPU")
            self._tab_refs["ram"] = ui.tab("RAM")
            self._tab_refs["disks"] = ui.tab("Disks")

        # Create tab panels
        with ui.tab_panels(tabs, value=self._tab_refs["cpu"]).classes("w-full"):
            with ui.tab_panel(self._tab_refs["cpu"]) as cpu_panel:
                self._tab_panels["cpu"] = cpu_panel
                if cpu:
                    self._cpu_component.render(cpu, self._show_per_core, self._toggle_cpu_view)
                else:
                    ui.label("No CPU data available").classes("text-sm text-gray-500")

            with ui.tab_panel(self._tab_refs["ram"]) as ram_panel:
                self._tab_panels["ram"] = ram_panel
                if memory:
                    self._memory_component.render(memory)
                else:
                    ui.label("No memory data available").classes("text-sm text-gray-500")

            with ui.tab_panel(self._tab_refs["disks"]) as disks_panel:
                self._tab_panels["disks"] = disks_panel
                if disks:
                    self._disk_component.render(disks)
                else:
                    ui.label("No disk data available").classes("text-sm text-gray-500")

    def _update_tab_contents(self, tile_data: dict) -> None:
        """Update tab contents without recreating structure"""
        if not tile_data:
            return

        cpu = tile_data.get("cpu")
        memory = tile_data.get("memory")
        disks = tile_data.get("disks", [])

        # Update CPU tab
        if cpu and "cpu" in self._tab_panels:
            self._tab_panels["cpu"].clear()
            with self._tab_panels["cpu"]:
                self._cpu_component.render(cpu, self._show_per_core, self._toggle_cpu_view)

        # Update RAM tab
        if memory and "ram" in self._tab_panels:
            self._tab_panels["ram"].clear()
            with self._tab_panels["ram"]:
                self._memory_component.render(memory)

        # Update Disks tab
        if disks and "disks" in self._tab_panels:
            self._tab_panels["disks"].clear()
            with self._tab_panels["disks"]:
                self._disk_component.render(disks)

    # -------------------------------------------------------------------------
    # Actions
    # -------------------------------------------------------------------------

    def _toggle_cpu_view(self) -> None:
        """Toggle between per-core and general CPU view"""
        self._show_per_core = not self._show_per_core
        self._preference_service.set_cpu_view_preference(self._show_per_core)

        # Force full refresh to apply new view
        self._tabs_initialized = False
        self._update_info()
