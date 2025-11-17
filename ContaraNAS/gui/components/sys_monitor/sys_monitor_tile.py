from nicegui import ui

from ContaraNAS.core.event_bus import event_bus
from ContaraNAS.core.utils import get_logger
from ContaraNAS.gui.components.base import BaseTile
from ContaraNAS.gui.components.base.base_view_model import BaseTileViewModel
from ContaraNAS.gui.components.sys_monitor import sys_monitor_tile_helper as helper
from ContaraNAS.modules.sys_monitor.constants import MAX_HISTORY_POINTS
from ContaraNAS.modules.sys_monitor.services import SysMonitorPreferenceService


logger = get_logger(__name__)


class SysMonitorTile(BaseTile):
    """System Monitor-specific module tile implementation"""

    module_type = "sys_monitor"

    def __init__(self, view_model, controller):
        self.cpu_core_history = {}
        self.cpu_general_history = []
        self.mem_history = []
        self.max_history_points = MAX_HISTORY_POINTS

        # Initialize preference service and load user preference for CPU view
        self.preference_service = SysMonitorPreferenceService()
        self.show_per_core = self.preference_service.get_cpu_view_preference()

        # Tab references - will be set during render
        self.cpu_tab_ref = None
        self.ram_tab_ref = None
        self.disks_tab_ref = None
        self.tabs_ref = None

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
        # Store current tab selection before clearing
        current_tab_value = None
        if self.tabs_ref is not None:
            try:
                current_tab_value = self.tabs_ref.value
            except:
                pass

        self.info_container.clear()

        with self.info_container:
            self.render(self.view_model.tile_data, current_tab_value)

    def _toggle_cpu_view(self):
        """Toggle between per-core and general CPU view"""
        self.show_per_core = not self.show_per_core
        self.preference_service.set_cpu_view_preference(self.show_per_core)

        # Force a refresh by updating the info container
        self.info_container.clear()
        with self.info_container:
            self.render(self.view_model.tile_data)

    def render(self, tile_data: dict, previous_tab=None):
        """Render System Monitor-specific stats in the tile with tabs"""
        if not tile_data:
            ui.label("No system data available").classes("text-sm text-gray-500")
            return

        cpu = tile_data.get("cpu")
        memory = tile_data.get("memory")
        disks = tile_data.get("disks", [])

        logger.debug(f"Rendering tile - CPU: {cpu is not None}, Memory: {memory is not None}, Disks: {len(disks) if disks else 0}")

        # Create tabs for CPU, RAM, and Disks
        with ui.tabs().classes('w-full') as tabs:
            self.cpu_tab_ref = ui.tab('CPU')
            self.ram_tab_ref = ui.tab('RAM')
            self.disks_tab_ref = ui.tab('Disks')

        # Store tabs reference
        self.tabs_ref = tabs

        # Restore previous tab selection
        initial_tab = self.cpu_tab_ref
        if previous_tab is not None:
            if previous_tab == self.ram_tab_ref or (hasattr(previous_tab, 'name') and previous_tab.name == 'RAM'):
                initial_tab = self.ram_tab_ref
            elif previous_tab == self.disks_tab_ref or (hasattr(previous_tab, 'name') and previous_tab.name == 'Disks'):
                initial_tab = self.disks_tab_ref

        with ui.tab_panels(tabs, value=initial_tab).classes('w-full'):
            # CPU Tab
            with ui.tab_panel(self.cpu_tab_ref):
                if cpu:
                    self._render_cpu_tab(cpu)
                else:
                    ui.label("No CPU data available").classes("text-sm text-gray-500")

            # RAM Tab
            with ui.tab_panel(self.ram_tab_ref):
                if memory:
                    self._render_ram_tab(memory)
                else:
                    ui.label("No memory data available").classes("text-sm text-gray-500")

            # Disks Tab
            with ui.tab_panel(self.disks_tab_ref):
                if disks:
                    self._render_disks_tab(disks)
                else:
                    ui.label("No disk data available").classes("text-sm text-gray-500")

    def _render_cpu_tab(self, cpu):
        """Render CPU information with graph-first layout"""
        # Add context menu for switching views
        with ui.context_menu():
            ui.menu_item(
                "Switch to General View" if self.show_per_core else "Switch to Per-Core View",
                on_click=self._toggle_cpu_view
            )

        # CPU name above graph
        ui.label(cpu.name).classes("text-sm font-semibold text-gray-700 mb-2")

        # Main graph section
        if self.show_per_core:
            # Per-core graphs in a grid
            self.cpu_core_history = helper.render_per_core_graphs(
                cpu, self.cpu_core_history, self.max_history_points
            )
        else:
            # General CPU graph
            self.cpu_general_history = helper.render_general_cpu_graph(
                cpu, self.cpu_general_history, self.max_history_points
            )

        # Main information below graph
        with ui.row().classes("w-full items-center gap-6 mb-2 mt-3"):
            # Primary metrics (larger, prominent)
            ui.label(f"Speed: {cpu.current_speed_ghz:.2f} GHz").classes("text-base font-bold text-gray-800")
            with ui.row().classes("items-center gap-1"):
                ui.label("Usage:").classes("text-base font-bold text-gray-800")
                ui.label(f"{cpu.total_usage:.1f}%").classes("text-base font-bold text-blue-600")

            # Format uptime as dd:hh:mm:ss
            days = int(cpu.uptime // 86400)
            hours = int((cpu.uptime % 86400) // 3600)
            minutes = int((cpu.uptime % 3600) // 60)
            seconds = int(cpu.uptime % 60)
            ui.label(f"Uptime: {days:02d}:{hours:02d}:{minutes:02d}:{seconds:02d}").classes("text-base font-bold text-gray-800")

        # Secondary information (regrouped in 2 columns, 3 rows)
        # Grid fills row-by-row, so order is: cores, threads, processes, min, max, FDs
        with ui.grid(columns=2).classes("w-full gap-x-8 gap-y-1 text-xs text-gray-600"):
            # Row 1
            ui.label(f"Cores: {cpu.physical_cores}P / {cpu.logical_cores}L")
            ui.label(f"Threads: {cpu.threads}")
            # Row 2
            ui.label(f"Processes: {cpu.processes}")
            ui.label(f"Min: {cpu.min_speed_ghz:.2f} GHz")
            # Row 3
            ui.label(f"Max: {cpu.max_speed_ghz:.2f} GHz")
            ui.label(f"FDs: {cpu.file_descriptors}")

    def _render_ram_tab(self, memory):
        """Render RAM information with graph-first layout"""
        # Calculate values
        total_gb = memory.total / (1024**3)
        used_gb = memory.used / (1024**3)
        available_gb = memory.available / (1024**3)
        free_gb = memory.free / (1024**3)
        buffers_gb = memory.buffers / (1024**3)
        cached_gb = memory.cached / (1024**3)
        shared_gb = memory.shared / (1024**3)
        swap_total_gb = memory.swap_total / (1024**3)
        swap_used_gb = memory.swap_used / (1024**3)

        # Main graph section
        # Memory graph
        self.mem_history.append(memory.usage)
        if len(self.mem_history) > self.max_history_points:
            self.mem_history.pop(0)

        fig = helper.create_plotly_graph(
            history=self.mem_history,
            color='#388e3c',
            height=150,
            max_range=100
        )
        ui.plotly(fig).classes("w-full")

        # Main information below graph
        with ui.row().classes("w-full items-center gap-6 mb-2 mt-3"):
            # Primary metrics
            with ui.row().classes("items-center gap-1"):
                ui.label("Usage:").classes("text-base font-bold text-gray-800")
                ui.label(f"{memory.usage:.1f}%").classes("text-base font-bold text-green-600")
            ui.label(f"Used: {used_gb:.1f} GB").classes("text-base font-bold text-gray-800")
            ui.label(f"Free: {free_gb:.1f} GB").classes("text-base font-bold text-gray-800")

        # Secondary information
        with ui.row().classes("w-full items-center gap-4 text-xs text-gray-600"):
            ui.label(f"Buffers: {buffers_gb:.1f} GB")
            ui.label(f"Cached: {cached_gb:.1f} GB")
            ui.label(f"Shared: {shared_gb:.1f} GB")
            ui.label(f"Swap: {swap_used_gb:.1f} / {swap_total_gb:.1f} GB ({memory.swap_usage:.1f}%)")

        # Physical RAM Sticks (if available)
        if memory.ram_sticks and len(memory.ram_sticks) > 0:
            ui.separator().classes("my-3")
            ui.label("Physical RAM Modules").classes("text-sm font-semibold mb-2")

            for i, ram in enumerate(memory.ram_sticks):
                with ui.row().classes("w-full items-center gap-2 mb-1 text-xs border border-black rounded p-2"):
                    ui.label(f"{i + 1}.").classes("w-4 text-gray-500")
                    ui.label(f"{ram.size:.0f}GB").classes("font-semibold w-12")
                    ui.label(ram.type).classes("w-16")
                    ui.label(f"{ram.speed} MT/s").classes("w-20")
                    ui.label(ram.locator).classes("w-16 text-gray-600")
                    ui.label(ram.manufacturer).classes("flex-1 text-gray-600 truncate")

    def _render_disks_tab(self, disks):
        """Render disk information with graph-first layout"""
        for i, disk in enumerate(disks):
            # Calculate speeds
            read_speed_mb = disk.read_speed / (1024**2)
            write_speed_mb = disk.write_speed / (1024**2)
            read_gb = disk.read_bytes / (1024**3)
            write_gb = disk.write_bytes / (1024**3)

            # Wrap each disk in a bordered container
            with ui.column().classes("w-full border border-black rounded p-3 mb-3"):
                # Disk header
                with ui.row().classes("w-full items-center gap-2 mb-2"):
                    ui.label(disk.mountpoint or disk.device).classes("text-sm font-bold")
                    ui.label(f"[{disk.type}]").classes("text-xs text-white bg-blue-500 px-1 py-0.5 rounded")
                    ui.label(disk.model).classes("flex-1 text-xs text-gray-600 truncate text-right")

                # Large usage bar
                with ui.row().classes("w-full items-center gap-2 mb-2"):
                    with ui.column().classes("flex-1"):
                        ui.linear_progress(disk.usage_percent / 100, show_value=False).props(
                            "color=orange size=20px"
                        )
                    ui.label(f"{disk.usage_percent:.1f}%").classes("text-base font-bold w-16 text-right")

                # Capacity info
                ui.label(f"{disk.used_gb:.1f} / {disk.total_gb:.1f} GB (Free: {disk.free_gb:.1f} GB)").classes("text-xs text-gray-600 mb-2")

                # Main information
                with ui.row().classes("w-full items-center gap-6 mb-1"):
                    # Primary metrics
                    ui.label(f"Read: {read_speed_mb:.1f} MB/s").classes("text-base font-bold text-gray-800")
                    ui.label(f"Write: {write_speed_mb:.1f} MB/s").classes("text-base font-bold text-gray-800")
                    ui.label(f"Busy: {disk.busy_time:.1f}%").classes("text-base font-bold text-orange-600")

                # Secondary information
                with ui.row().classes("w-full items-center gap-4 text-xs text-gray-600"):
                    ui.label(f"Device: {disk.device}")
                    ui.label(f"FS: {disk.filesystem}")
                    ui.label(f"Total Read: {read_gb:.1f} GB")
                    ui.label(f"Total Write: {write_gb:.1f} GB")
                    ui.label(f"I/O Time: {disk.io_time} ms")
