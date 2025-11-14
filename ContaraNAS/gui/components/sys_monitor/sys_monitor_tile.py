from nicegui import ui
import plotly.graph_objects as go

from ContaraNAS.core.utils import get_logger
from ContaraNAS.gui.components.base import BaseTile


logger = get_logger(__name__)


class SysMonitorTile(BaseTile):
    """System Monitor-specific module tile implementation"""

    module_type = "sys_monitor"

    def __init__(self, view_model, controller):
        super().__init__(view_model, controller)
        self.cpu_core_history = {}  # Track history per core
        self.cpu_general_history = []  # Track general CPU history
        self.mem_history = []
        self.max_history_points = 30
        self.show_per_core = True  # Toggle between per-core and general CPU view

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
            self._render_memory_section(memory)

        # Disk Section with bars
        if disks:
            self._render_disk_summary(disks)

    def _toggle_cpu_view(self):
        """Toggle between per-core and general CPU view"""
        self.show_per_core = not self.show_per_core
        # Force a refresh by updating the info container
        self.info_container.clear()
        with self.info_container:
            self.render(self.view_model.tile_data)

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
            with ui.row().classes("w-full items-center justify-between mb-2"):
                ui.label("CPU").classes("text-xs font-semibold text-black")
                ui.label(f"{cpu.total_usage:.0f}%").classes("text-xs font-bold min-w-fit text-blue-500")

            if self.show_per_core:
                # Per-core graphs in a grid
                self._render_per_core_graphs(cpu)
            else:
                # General CPU graph
                self._render_general_cpu_graph(cpu)

            # CPU details
            ui.label(f"{cpu.physical_cores}C/{cpu.logical_cores}T @ {cpu.current_speed_ghz:.2f}GHz").classes(
                "text-xs text-gray-500 mt-1"
            )

    def _render_per_core_graphs(self, cpu):
        """Render individual graphs for each CPU core"""
        num_cores = len(cpu.usage_per_core)
        cols = min(4, num_cores)  # Max 4 columns

        with ui.grid(columns=cols).classes("w-full gap-1"):
            for i, core_usage in enumerate(cpu.usage_per_core):
                # Track history for this core
                if i not in self.cpu_core_history:
                    self.cpu_core_history[i] = []

                self.cpu_core_history[i].append(core_usage)
                if len(self.cpu_core_history[i]) > self.max_history_points:
                    self.cpu_core_history[i].pop(0)

                # Create mini graph for this core
                with ui.column().classes("w-full"):
                    # Core label with usage
                    ui.label(f"Core {i}: {core_usage:.0f}%").classes("text-[10px] text-black")

                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        y=self.cpu_core_history[i],
                        mode='lines',
                        fill='tozeroy',
                        line=dict(color='#1976d2', width=1),
                        fillcolor='rgba(25, 118, 210, 0.3)',
                        hovertemplate='%{y:.1f}%<extra></extra>'
                    ))
                    fig.update_layout(
                        height=50,
                        margin=dict(l=0, r=0, t=0, b=0),
                        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
                        yaxis=dict(showgrid=False, showticklabels=False, zeroline=False, range=[0, 100]),
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        showlegend=False,
                        hovermode='closest'
                    )
                    ui.plotly(fig).classes("w-full").props('config="{displayModeBar: false, displaylogo: false}"')

    def _render_general_cpu_graph(self, cpu):
        """Render single general CPU usage graph"""
        # Track general CPU history
        self.cpu_general_history.append(cpu.total_usage)
        if len(self.cpu_general_history) > self.max_history_points:
            self.cpu_general_history.pop(0)

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            y=self.cpu_general_history,
            mode='lines',
            fill='tozeroy',
            line=dict(color='#1976d2', width=1),
            fillcolor='rgba(25, 118, 210, 0.3)',
            hovertemplate='%{y:.1f}%<extra></extra>'
        ))
        fig.update_layout(
            height=100,
            margin=dict(l=0, r=0, t=0, b=0),
            xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
            yaxis=dict(showgrid=False, showticklabels=False, zeroline=False, range=[0, 100]),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            showlegend=False,
            hovermode='closest'
        )
        ui.plotly(fig).classes("w-full").props('config="{displayModeBar: false, displaylogo: false}"')

    def _render_memory_section(self, memory):
        """Render memory information with Task Manager style graph"""
        with ui.column().classes("w-full mb-3"):
            # Header with usage percentage
            with ui.row().classes("w-full items-center justify-between"):
                ui.label("Memory").classes("text-xs font-semibold text-black")
                ui.label(f"{memory.usage:.0f}%").classes("text-xs font-bold min-w-fit text-green-600")

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
                fillcolor='rgba(56, 142, 60, 0.3)',
                hovertemplate='%{y:.1f}%<extra></extra>'
            ))
            fig.update_layout(
                height=80,
                margin=dict(l=0, r=0, t=0, b=0),
                xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
                yaxis=dict(showgrid=False, showticklabels=False, zeroline=False, range=[0, 100]),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                showlegend=False,
                hovermode='closest'
            )
            ui.plotly(fig).classes("w-full").props('config="{displayModeBar: false, displaylogo: false}"')

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
            ui.label("Disks").classes("text-xs font-semibold text-black mb-1")

            # Show only the first 3 disks in the tile
            for disk in disks[:3]:
                with ui.row().classes("w-full items-center gap-2 mb-1"):
                    # Mount point label
                    ui.label(disk.mountpoint).classes("text-xs w-20 truncate text-black")

                    # Disk usage bar
                    with ui.column().classes("flex-1"):
                        ui.linear_progress(disk.usage_percent / 100, show_value=False).props("color=orange size=8px")

                    # Usage percentage
                    ui.label(f"{disk.usage_percent:.0f}%").classes("text-xs font-mono w-10 text-right text-black")

            # Show count if more disks exist
            if len(disks) > 3:
                ui.label(f"+ {len(disks) - 3} more disk(s)").classes(
                    "text-xs text-gray-500 mt-1"
                )
