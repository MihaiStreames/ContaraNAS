from nicegui import ui

from ContaraNAS.core.utils import get_logger
from ContaraNAS.core.utils.cache_utils import get_cache_dir, load_json, save_json
from ContaraNAS.gui.components.base import BaseTile
from ContaraNAS.gui.components.sys_monitor import sys_monitor_tile_helper as helper


logger = get_logger(__name__)

# Cache file for user preferences
PREFERENCES_CACHE_FILE = get_cache_dir() / "sys_monitor_preferences.json"


class SysMonitorTile(BaseTile):
    """System Monitor-specific module tile implementation"""

    module_type = "sys_monitor"

    def __init__(self, view_model, controller):
        super().__init__(view_model, controller)
        self.cpu_core_history = {}  # Track history per core
        self.cpu_general_history = []  # Track general CPU history
        self.mem_history = []
        self.max_history_points = 30

        # Load user preference for CPU view (default to per-core)
        self.show_per_core = self._load_cpu_view_preference()

    def _load_cpu_view_preference(self) -> bool:
        """Load the user's CPU view preference from cache"""
        try:
            prefs = load_json(PREFERENCES_CACHE_FILE)
            if prefs and "show_per_core" in prefs:
                return prefs["show_per_core"]
        except Exception as e:
            logger.debug(f"Could not load CPU view preference: {e}")

        # Default to per-core view
        return True

    def _save_cpu_view_preference(self) -> None:
        """Save the user's CPU view preference to cache"""
        try:
            prefs = load_json(PREFERENCES_CACHE_FILE) or {}
            prefs["show_per_core"] = self.show_per_core
            save_json(PREFERENCES_CACHE_FILE, prefs)
        except Exception as e:
            logger.error(f"Could not save CPU view preference: {e}")

    def _toggle_cpu_view(self):
        """Toggle between per-core and general CPU view"""
        self.show_per_core = not self.show_per_core
        self._save_cpu_view_preference()

        # Force a refresh by updating the info container
        self.info_container.clear()
        with self.info_container:
            self.render(self.view_model.tile_data)

    def render(self, tile_data: dict):
        """Render System Monitor-specific stats in the tile"""
        if not tile_data:
            ui.label("No system data available").classes("text-sm text-gray-500")
            return

        cpu = tile_data.get("cpu")
        memory = tile_data.get("memory")
        disks = tile_data.get("disks", [])

        logger.debug(f"Rendering tile - CPU: {cpu is not None}, Memory: {memory is not None}, Disks: {len(disks) if disks else 0}")

        # CPU Section with switchable graphs
        if cpu:
            self._render_cpu_section(cpu)

        # Memory Section with graph
        if memory:
            self.mem_history = helper.render_memory_section(memory, self.mem_history, self.max_history_points)

        # Disk Section with bars
        if disks:
            helper.render_disk_summary(disks)

    def _render_cpu_section(self, cpu):
        """Render CPU information with switchable graphs"""
        with ui.column().classes("w-full mb-3"):
            # Add context menu for switching views
            with ui.context_menu():
                ui.menu_item(
                    "Switch to General View" if self.show_per_core else "Switch to Per-Core View",
                    on_click=self._toggle_cpu_view
                )

            # Header with overall usage percentage
            helper.render_cpu_header(cpu.total_usage)

            if self.show_per_core:
                # Per-core graphs in a grid
                self.cpu_core_history = helper.render_per_core_graphs(
                    cpu, self.cpu_core_history, self.max_history_points
                )
            else:
                # General CPU graph
                self.cpu_general_history = helper.render_general_cpu_graph(
                    cpu.total_usage, self.cpu_general_history, self.max_history_points
                )

            # CPU details
            helper.render_cpu_details(cpu.physical_cores, cpu.logical_cores, cpu.current_speed_ghz)
