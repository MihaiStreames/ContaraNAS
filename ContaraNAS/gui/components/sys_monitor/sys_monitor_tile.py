from nicegui import ui
from nicegui.elements.plotly import Plotly
import plotly.graph_objects as go

from ContaraNAS.core.utils import get_logger
from ContaraNAS.gui.components.base import BaseTile


logger = get_logger(__name__)


class SysMonitorTile(BaseTile):
    """System Monitor-specific module tile implementation"""

    module_type = "sys_monitor"

    def __init__(self, view_model, controller):
        super().__init__(view_model, controller)
        self.cpu_history = []
        self.mem_history = []
        self.max_history_points = 30

    def render(self, tile_data: dict):
        """Render System Monitor-specific stats in the tile"""
        if not tile_data:
            ui.label("No system data available").classes("text-sm text-gray-500")
            return

        cpu = tile_data.get("cpu")
        memory = tile_data.get("memory")
        disks = tile_data.get("disks", [])

        logger.debug(f"Rendering tile - CPU: {cpu is not None}, Memory: {memory is not None}, Disks: {len(disks) if disks else 0}")

        # CPU Section with graph
        if cpu:
            self._render_cpu_section(cpu)

        # Memory Section with graph
        if memory:
            self._render_memory_section(memory)

        # Disk Section with bars
        if disks:
            self._render_disk_summary(disks)

    def _render_cpu_section(self, cpu):
        """Render CPU information with Task Manager style graph"""
        with ui.column().classes("w-full mb-3"):
            # Header with usage percentage
            with ui.row().classes("w-full items-center justify-between"):
                ui.label("CPU").classes("text-xs font-semibold text-gray-400")
                ui.label(f"{cpu.total_usage:.0f}%").classes("text-sm font-bold text-blue-500")

            # Simple mini graph using plotly
            self.cpu_history.append(cpu.total_usage)
            if len(self.cpu_history) > self.max_history_points:
                self.cpu_history.pop(0)

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                y=self.cpu_history,
                mode='lines',
                fill='tozeroy',
                line=dict(color='#1976d2', width=1),
                fillcolor='rgba(25, 118, 210, 0.3)'
            ))
            fig.update_layout(
                height=80,
                margin=dict(l=0, r=0, t=0, b=0),
                xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
                yaxis=dict(showgrid=False, showticklabels=False, zeroline=False, range=[0, 100]),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                showlegend=False
            )
            ui.plotly(fig).classes("w-full")

            # CPU details
            ui.label(f"{cpu.physical_cores}C/{cpu.logical_cores}T @ {cpu.current_speed_ghz:.2f}GHz").classes(
                "text-xs text-gray-500"
            )

    def _render_memory_section(self, memory):
        """Render memory information with Task Manager style graph"""
        with ui.column().classes("w-full mb-3"):
            # Header with usage percentage
            with ui.row().classes("w-full items-center justify-between"):
                ui.label("Memory").classes("text-xs font-semibold text-gray-400")
                ui.label(f"{memory.usage:.0f}%").classes("text-sm font-bold text-green-600")

            # Simple mini graph using plotly
            self.mem_history.append(memory.usage)
            if len(self.mem_history) > self.max_history_points:
                self.mem_history.pop(0)

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                y=self.mem_history,
                mode='lines',
                fill='tozeroy',
                line=dict(color='#388e3c', width=1),
                fillcolor='rgba(56, 142, 60, 0.3)'
            ))
            fig.update_layout(
                height=80,
                margin=dict(l=0, r=0, t=0, b=0),
                xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
                yaxis=dict(showgrid=False, showticklabels=False, zeroline=False, range=[0, 100]),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                showlegend=False
            )
            ui.plotly(fig).classes("w-full")

            # Memory details
            used_gb = memory.used / (1024**3)
            total_gb = memory.total / (1024**3)
            ui.label(f"{used_gb:.1f}GB / {total_gb:.1f}GB").classes(
                "text-xs text-gray-500"
            )

    @staticmethod
    def _render_disk_summary(disks):
        """Render disk summary with progress bars"""
        with ui.column().classes("w-full"):
            ui.label("Disks").classes("text-xs font-semibold text-gray-400 mb-1")

            # Show only the first 3 disks in the tile
            for disk in disks[:3]:
                with ui.row().classes("w-full items-center gap-2 mb-1"):
                    # Mount point label
                    ui.label(disk.mountpoint).classes("text-xs w-20 truncate text-gray-500")

                    # Disk usage bar
                    with ui.column().classes("flex-1"):
                        ui.linear_progress(disk.usage_percent / 100, show_value=False).props("color=orange size=8px")

                    # Usage percentage
                    ui.label(f"{disk.usage_percent:.0f}%").classes("text-xs font-mono w-10 text-right")

            # Show count if more disks exist
            if len(disks) > 3:
                ui.label(f"+ {len(disks) - 3} more disk(s)").classes(
                    "text-xs text-gray-500 mt-1"
                )
