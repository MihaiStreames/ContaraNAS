import platform

from nicegui import ui

from ContaraNAS.gui.components.shared import TimeSeriesGraph
from ContaraNAS.gui.components.shared.formatters import format_duration, format_frequency
from ContaraNAS.gui.components.shared.graphs import GraphConfig, PerCoreGraphGrid
from ContaraNAS.gui.components.shared.stats import primary_stats_row, secondary_stats_grid
from ContaraNAS.modules.sys_monitor.constants import (
    CPU_GRAPH_HEIGHT,
    MAX_HISTORY_POINTS,
    PER_CORE_GRAPH_HEIGHT,
)
from ContaraNAS.modules.sys_monitor.dtos import CPUInfo


class CPUStatsComponent:
    """Reusable CPU stats display component"""

    def __init__(self, max_history: int = MAX_HISTORY_POINTS):
        self.max_history = max_history

        # Graph components
        self._general_graph: TimeSeriesGraph | None = None
        self._per_core_grid: PerCoreGraphGrid | None = None

        # State
        self._current_cpu: CPUInfo | None = None
        self._show_per_core: bool = True

    def _get_general_graph(self) -> TimeSeriesGraph:
        """Lazy initialization of general CPU graph"""
        if self._general_graph is None:
            self._general_graph = TimeSeriesGraph(
                GraphConfig(color="#1976d2", height=CPU_GRAPH_HEIGHT),
                max_points=self.max_history,
            )
        return self._general_graph

    def _get_per_core_grid(self, num_cores: int) -> PerCoreGraphGrid:
        """Lazy initialization of per-core grid"""
        if self._per_core_grid is None or self._per_core_grid.num_cores != num_cores:
            self._per_core_grid = PerCoreGraphGrid(
                num_cores=num_cores,
                config=GraphConfig(color="#1976d2", height=PER_CORE_GRAPH_HEIGHT),
                max_points=self.max_history,
            )
        return self._per_core_grid

    def render(
        self,
        cpu: CPUInfo,
        show_per_core: bool,
        on_toggle_view: callable,
    ) -> None:
        """Render CPU stats with graphs and info"""
        self._current_cpu = cpu
        self._show_per_core = show_per_core

        # Context menu for view toggle
        with ui.context_menu():
            toggle_label = "Switch to General View" if show_per_core else "Switch to Per-Core View"
            ui.menu_item(toggle_label, on_click=on_toggle_view)

        # CPU name header
        ui.label(cpu.name).classes("text-base font-bold text-gray-700 mb-2")

        # Graph section
        if show_per_core:
            grid = self._get_per_core_grid(len(cpu.usage_per_core))
            grid.render()
            grid.update(cpu.usage_per_core)
        else:
            graph = self._get_general_graph()
            graph.render()
            graph.update(cpu.total_usage)

        # Primary stats row
        primary_stats_row(
            [
                ("Speed", format_frequency(cpu.current_speed_ghz), False),
                ("Usage", f"{cpu.total_usage:.1f}%", True),
                ("Uptime", format_duration(cpu.uptime), False),
            ]
        )

        # Secondary stats grid
        fd_label = "Handles" if platform.system() == "Windows" else "File Descriptors"
        secondary_stats_grid(
            [
                ("Cores", f"{cpu.physical_cores}P / {cpu.logical_cores}L"),
                ("Threads", str(cpu.threads)),
                ("Max", format_frequency(cpu.max_speed_ghz)),
                ("Processes", str(cpu.processes)),
                ("Min", format_frequency(cpu.min_speed_ghz)),
                (fd_label, str(cpu.file_descriptors)),
            ]
        )
