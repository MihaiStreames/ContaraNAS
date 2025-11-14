from nicegui import ui

from ContaraNAS.gui.components.base import BaseTile


class SysMonitorTile(BaseTile):
    """System Monitor-specific module tile implementation"""

    module_type = "sys_monitor"

    def __init__(self, view_model, controller):
        super().__init__(view_model, controller)

    def render(self, tile_data: dict):
        """Render System Monitor-specific stats in the tile"""
        if not tile_data:
            ui.label("No system data available").classes("text-sm text-gray-500")
            return

        cpu = tile_data.get("cpu")
        memory = tile_data.get("memory")
        disks = tile_data.get("disks", [])

        # CPU Section
        if cpu:
            self._render_cpu_section(cpu)

        # Memory Section
        if memory:
            self._render_memory_section(memory)

        # Disk Section
        if disks:
            self._render_disk_summary(disks)

    @staticmethod
    def _render_cpu_section(cpu):
        """Render CPU information"""
        with ui.column().classes("w-full mb-2"):
            ui.label("CPU").classes("text-xs font-semibold text-gray-400 mb-1")

            # CPU usage bar
            ui.linear_progress(cpu.total_usage / 100, color="blue").classes("h-2")

            # CPU details
            ui.label(f"{cpu.physical_cores}C/{cpu.logical_cores}T @ {cpu.current_speed_ghz:.2f}GHz").classes(
                "text-xs text-gray-500"
            )

    @staticmethod
    def _render_memory_section(memory):
        """Render memory information"""
        with ui.column().classes("w-full mb-2"):
            ui.label("Memory").classes("text-xs font-semibold text-gray-400 mb-1")

            # Memory usage bar
            ui.linear_progress(memory.usage / 100, color="green").classes("h-2")

            # Memory details
            ui.label(f"{memory.used_gb:.1f}GB / {memory.total_gb:.1f}GB").classes(
                "text-xs text-gray-500"
            )

    @staticmethod
    def _render_disk_summary(disks):
        """Render disk summary"""
        with ui.column().classes("w-full"):
            ui.label("Disks").classes("text-xs font-semibold text-gray-400 mb-1")

            # Show only the first 3 disks in the tile
            for disk in disks[:3]:
                with ui.column().classes("w-full mb-1"):
                    # Mount point label
                    ui.label(disk.mountpoint).classes("text-xs text-gray-500")

                    # Disk usage bar
                    ui.linear_progress(disk.usage_percent / 100, color="orange").classes("h-2")

            # Show count if more disks exist
            if len(disks) > 3:
                ui.label(f"+ {len(disks) - 3} more disk(s)").classes(
                    "text-xs text-gray-500 mt-1"
                )
