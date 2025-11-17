from nicegui import ui

from ContaraNAS.core.utils import get_logger
from ContaraNAS.gui.components.base import BaseTile
from ContaraNAS.gui.components.sys_monitor import sys_monitor_tile_helper as helper
from ContaraNAS.modules.sys_monitor.constants import MAX_HISTORY_POINTS
from ContaraNAS.modules.sys_monitor.services import SysMonitorPreferenceService


logger = get_logger(__name__)


class SysMonitorTile(BaseTile):
    """System Monitor-specific module tile implementation"""

    module_type = "sys_monitor"

    def __init__(self, view_model, controller):
        super().__init__(view_model, controller)
        self.cpu_core_history = {}
        self.cpu_general_history = []
        self.mem_history = []
        self.max_history_points = MAX_HISTORY_POINTS

        # Initialize preference service and load user preference for CPU view
        self.preference_service = SysMonitorPreferenceService()
        self.show_per_core = self.preference_service.get_cpu_view_preference()

    def _toggle_cpu_view(self):
        """Toggle between per-core and general CPU view"""
        self.show_per_core = not self.show_per_core
        self.preference_service.set_cpu_view_preference(self.show_per_core)

        # Force a refresh by updating the info container
        self.info_container.clear()
        with self.info_container:
            self.render(self.view_model.tile_data)

    def render(self, tile_data: dict):
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
            cpu_tab = ui.tab('CPU')
            ram_tab = ui.tab('RAM')
            disks_tab = ui.tab('Disks')

        with ui.tab_panels(tabs, value=cpu_tab).classes('w-full'):
            # CPU Tab
            with ui.tab_panel(cpu_tab):
                if cpu:
                    self._render_cpu_tab(cpu)
                else:
                    ui.label("No CPU data available").classes("text-sm text-gray-500")

            # RAM Tab
            with ui.tab_panel(ram_tab):
                if memory:
                    self._render_ram_tab(memory)
                else:
                    ui.label("No memory data available").classes("text-sm text-gray-500")

            # Disks Tab
            with ui.tab_panel(disks_tab):
                if disks:
                    self._render_disks_tab(disks)
                else:
                    ui.label("No disk data available").classes("text-sm text-gray-500")

    def _render_cpu_tab(self, cpu):
        """Render comprehensive CPU information in dedicated tab"""
        with ui.column().classes("w-full"):
            # Add context menu for switching views
            with ui.context_menu():
                ui.menu_item(
                    "Switch to General View" if self.show_per_core else "Switch to Per-Core View",
                    on_click=self._toggle_cpu_view
                )

            # CPU Header Section
            with ui.card().classes("w-full mb-3 p-3"):
                ui.label("CPU Information").classes("text-sm font-bold mb-2")

                # CPU Name and Model
                ui.label(cpu.name).classes("text-xs font-semibold text-gray-700 mb-2")

                # Usage indicator
                with ui.row().classes("w-full items-center gap-2 mb-2"):
                    ui.label("Total Usage:").classes("text-xs text-gray-600")
                    ui.label(f"{cpu.total_usage:.1f}%").classes("text-lg font-bold text-blue-500")

                # Core and thread information
                with ui.grid(columns=2).classes("w-full gap-2 text-xs"):
                    ui.label("Physical Cores:").classes("text-gray-600")
                    ui.label(f"{cpu.physical_cores}").classes("font-semibold")

                    ui.label("Logical Cores:").classes("text-gray-600")
                    ui.label(f"{cpu.logical_cores}").classes("font-semibold")

                    ui.label("Current Speed:").classes("text-gray-600")
                    ui.label(f"{cpu.current_speed_ghz:.2f} GHz").classes("font-semibold")

                    ui.label("Max Speed:").classes("text-gray-600")
                    ui.label(f"{cpu.max_speed_ghz:.2f} GHz").classes("font-semibold")

                    ui.label("Min Speed:").classes("text-gray-600")
                    ui.label(f"{cpu.min_speed_ghz:.2f} GHz").classes("font-semibold")

                    ui.label("Processes:").classes("text-gray-600")
                    ui.label(f"{cpu.processes}").classes("font-semibold")

                    ui.label("Threads:").classes("text-gray-600")
                    ui.label(f"{cpu.threads}").classes("font-semibold")

                    ui.label("File Descriptors:").classes("text-gray-600")
                    ui.label(f"{cpu.file_descriptors}").classes("font-semibold")

                    ui.label("System Uptime:").classes("text-gray-600")
                    uptime_hours = cpu.uptime / 3600
                    ui.label(f"{uptime_hours:.1f} hours").classes("font-semibold")

            # CPU Graphs Section
            with ui.card().classes("w-full p-3"):
                ui.label("CPU Usage Graphs").classes("text-sm font-bold mb-2")

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

    def _render_ram_tab(self, memory):
        """Render comprehensive RAM information in dedicated tab"""
        with ui.column().classes("w-full"):
            # Memory Usage Section
            with ui.card().classes("w-full mb-3 p-3"):
                ui.label("Memory Usage").classes("text-sm font-bold mb-2")

                # Usage indicator
                with ui.row().classes("w-full items-center gap-2 mb-2"):
                    ui.label("Usage:").classes("text-xs text-gray-600")
                    ui.label(f"{memory.usage:.1f}%").classes("text-lg font-bold text-green-600")

                # Memory graph
                self.mem_history.append(memory.usage)
                if len(self.mem_history) > self.max_history_points:
                    self.mem_history.pop(0)

                fig = helper.create_plotly_graph(
                    history=self.mem_history,
                    color='#388e3c',
                    height=100,
                    max_range=100
                )
                ui.plotly(fig).classes("w-full")

                # Memory details
                with ui.grid(columns=2).classes("w-full gap-2 text-xs mt-3"):
                    total_gb = memory.total / (1024**3)
                    used_gb = memory.used / (1024**3)
                    available_gb = memory.available / (1024**3)
                    free_gb = memory.free / (1024**3)
                    buffers_gb = memory.buffers / (1024**3)
                    cached_gb = memory.cached / (1024**3)
                    shared_gb = memory.shared / (1024**3)

                    ui.label("Total:").classes("text-gray-600")
                    ui.label(f"{total_gb:.2f} GB").classes("font-semibold")

                    ui.label("Used:").classes("text-gray-600")
                    ui.label(f"{used_gb:.2f} GB").classes("font-semibold")

                    ui.label("Available:").classes("text-gray-600")
                    ui.label(f"{available_gb:.2f} GB").classes("font-semibold")

                    ui.label("Free:").classes("text-gray-600")
                    ui.label(f"{free_gb:.2f} GB").classes("font-semibold")

                    ui.label("Buffers:").classes("text-gray-600")
                    ui.label(f"{buffers_gb:.2f} GB").classes("font-semibold")

                    ui.label("Cached:").classes("text-gray-600")
                    ui.label(f"{cached_gb:.2f} GB").classes("font-semibold")

                    ui.label("Shared:").classes("text-gray-600")
                    ui.label(f"{shared_gb:.2f} GB").classes("font-semibold")

            # Swap Information Section
            with ui.card().classes("w-full mb-3 p-3"):
                ui.label("Swap Memory").classes("text-sm font-bold mb-2")

                with ui.grid(columns=2).classes("w-full gap-2 text-xs"):
                    swap_total_gb = memory.swap_total / (1024**3)
                    swap_used_gb = memory.swap_used / (1024**3)
                    swap_free_gb = memory.swap_free / (1024**3)

                    ui.label("Total:").classes("text-gray-600")
                    ui.label(f"{swap_total_gb:.2f} GB").classes("font-semibold")

                    ui.label("Used:").classes("text-gray-600")
                    ui.label(f"{swap_used_gb:.2f} GB").classes("font-semibold")

                    ui.label("Free:").classes("text-gray-600")
                    ui.label(f"{swap_free_gb:.2f} GB").classes("font-semibold")

                    ui.label("Usage:").classes("text-gray-600")
                    ui.label(f"{memory.swap_usage:.1f}%").classes("font-semibold")

            # Physical RAM Sticks Section
            if memory.ram_sticks and len(memory.ram_sticks) > 0:
                with ui.card().classes("w-full p-3"):
                    ui.label("Physical RAM Modules").classes("text-sm font-bold mb-2")

                    for i, ram in enumerate(memory.ram_sticks):
                        with ui.card().classes("w-full mb-2 p-2 bg-gray-50"):
                            ui.label(f"Module {i + 1}").classes("text-xs font-bold mb-1")

                            with ui.grid(columns=2).classes("w-full gap-1 text-xs"):
                                ui.label("Locator:").classes("text-gray-600")
                                ui.label(ram.locator).classes("font-semibold")

                                ui.label("Bank:").classes("text-gray-600")
                                ui.label(ram.bank_locator).classes("font-semibold")

                                ui.label("Size:").classes("text-gray-600")
                                ui.label(f"{ram.size:.0f} GB").classes("font-semibold")

                                ui.label("Type:").classes("text-gray-600")
                                ui.label(ram.type).classes("font-semibold")

                                ui.label("Speed:").classes("text-gray-600")
                                ui.label(f"{ram.speed} MT/s").classes("font-semibold")

                                ui.label("Manufacturer:").classes("text-gray-600")
                                ui.label(ram.manufacturer).classes("font-semibold")

                                ui.label("Part Number:").classes("text-gray-600")
                                ui.label(ram.part_number).classes("font-semibold")

    def _render_disks_tab(self, disks):
        """Render comprehensive disk information in dedicated tab"""
        with ui.column().classes("w-full"):
            ui.label("Disk Drives").classes("text-sm font-bold mb-2")

            for disk in disks:
                with ui.card().classes("w-full mb-3 p-3"):
                    # Disk header with mountpoint and type
                    with ui.row().classes("w-full items-center gap-2 mb-2"):
                        ui.label(disk.mountpoint or disk.device).classes("text-sm font-bold")
                        ui.label(f"[{disk.type}]").classes("text-xs text-white bg-blue-500 px-2 py-1 rounded")

                    # Model and device
                    ui.label(disk.model).classes("text-xs text-gray-600 mb-2")

                    # Usage bar
                    with ui.row().classes("w-full items-center gap-2 mb-2"):
                        with ui.column().classes("flex-1"):
                            ui.linear_progress(disk.usage_percent / 100, show_value=False).props(
                                "color=orange size=12px"
                            )
                        ui.label(f"{disk.usage_percent:.1f}%").classes("text-sm font-bold")

                    # Storage capacity
                    ui.label(f"{disk.used_gb:.1f} GB used of {disk.total_gb:.1f} GB ({disk.free_gb:.1f} GB free)").classes(
                        "text-xs text-gray-600 mb-2"
                    )

                    # Detailed information
                    with ui.grid(columns=2).classes("w-full gap-2 text-xs"):
                        ui.label("Device:").classes("text-gray-600")
                        ui.label(disk.device).classes("font-semibold")

                        ui.label("Filesystem:").classes("text-gray-600")
                        ui.label(disk.filesystem).classes("font-semibold")

                        ui.label("Read Speed:").classes("text-gray-600")
                        read_speed_mb = disk.read_speed / (1024**2)
                        ui.label(f"{read_speed_mb:.2f} MB/s").classes("font-semibold")

                        ui.label("Write Speed:").classes("text-gray-600")
                        write_speed_mb = disk.write_speed / (1024**2)
                        ui.label(f"{write_speed_mb:.2f} MB/s").classes("font-semibold")

                        ui.label("Total Read:").classes("text-gray-600")
                        read_gb = disk.read_bytes / (1024**3)
                        ui.label(f"{read_gb:.2f} GB").classes("font-semibold")

                        ui.label("Total Written:").classes("text-gray-600")
                        write_gb = disk.write_bytes / (1024**3)
                        ui.label(f"{write_gb:.2f} GB").classes("font-semibold")

                        ui.label("Read Time:").classes("text-gray-600")
                        ui.label(f"{disk.read_time} ms").classes("font-semibold")

                        ui.label("Write Time:").classes("text-gray-600")
                        ui.label(f"{disk.write_time} ms").classes("font-semibold")

                        ui.label("I/O Time:").classes("text-gray-600")
                        ui.label(f"{disk.io_time} ms").classes("font-semibold")

                        ui.label("Busy Time:").classes("text-gray-600")
                        ui.label(f"{disk.busy_time:.1f}%").classes("font-semibold")
