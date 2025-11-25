from nicegui import ui

from ContaraNAS.gui.components.shared import bordered_section, stat_label, usage_bar
from ContaraNAS.gui.components.shared.stats import secondary_stats_grid
from ContaraNAS.modules.sys_monitor.dtos import DiskInfo


class DiskStatsComponent:
    """Reusable disk stats display component"""

    def render(self, disks: list[DiskInfo]) -> None:
        """Render all disk information"""
        for disk in disks:
            self._render_single_disk(disk)

    @staticmethod
    def _render_single_disk(disk: DiskInfo) -> None:
        """Render a single disk's information"""
        # Calculate speeds
        read_speed_mb = disk.read_speed / (1024**2)
        write_speed_mb = disk.write_speed / (1024**2)
        read_gb = disk.read_bytes / (1024**3)
        write_gb = disk.write_bytes / (1024**3)

        with bordered_section():
            # Header row
            with ui.row().classes("w-full items-center gap-2 mb-2"):
                ui.label(disk.mountpoint or disk.device).classes("text-base font-bold")
                ui.badge(disk.type).props("color=blue")
                ui.label(disk.model).classes("flex-1 text-xs text-gray-600 truncate text-right")

            # Usage bar
            usage_bar(disk.usage_percent, color="orange")

            # Capacity info
            ui.label(
                f"{disk.used_gb:.1f} / {disk.total_gb:.1f} GB (Free: {disk.free_gb:.1f} GB)"
            ).classes("text-xs text-gray-600 mb-2")

            # Speed stats
            with ui.row().classes("w-full items-center gap-6 mb-1"):
                stat_label("Read", f"{read_speed_mb:.1f}", unit=" MB/s", size="text-sm")
                stat_label("Write", f"{write_speed_mb:.1f}", unit=" MB/s", size="text-sm")
                stat_label("Busy", f"{disk.busy_time:.1f}%", "text-orange-600", size="text-sm")

            # Secondary info
            secondary_stats_grid(
                [
                    ("Device", disk.device),
                    ("Total Write", f"{write_gb:.1f} GB"),
                    ("I/O Time", f"{disk.io_time} ms"),
                    ("FS", disk.filesystem),
                    ("Total Read", f"{read_gb:.1f} GB"),
                ],
                columns=3,
            )
