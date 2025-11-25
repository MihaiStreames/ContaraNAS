from nicegui import ui

from ContaraNAS.gui.components.shared import GraphConfig, TimeSeriesGraph
from ContaraNAS.gui.components.shared.stats import primary_stats_row
from ContaraNAS.modules.sys_monitor.constants import MAX_HISTORY_POINTS, MEMORY_GRAPH_HEIGHT
from ContaraNAS.modules.sys_monitor.dtos import MemoryInfo


class MemoryStatsComponent:
    """Reusable memory stats display component"""

    def __init__(self, max_history: int = MAX_HISTORY_POINTS):
        self.max_history = max_history
        self._graph: TimeSeriesGraph | None = None

    def _get_graph(self) -> TimeSeriesGraph:
        """Lazy initialization of memory graph"""
        if self._graph is None:
            self._graph = TimeSeriesGraph(
                GraphConfig(color="#388e3c", height=MEMORY_GRAPH_HEIGHT),
                max_points=self.max_history,
            )
        return self._graph

    def render(self, memory: MemoryInfo) -> None:
        """Render memory stats with graph and info"""
        # Graph
        graph = self._get_graph()
        graph.render()
        graph.update(memory.usage)

        # Calculate display values
        used_gb = memory.used / (1024**3)
        free_gb = memory.free / (1024**3)
        buffers_gb = memory.buffers / (1024**3)
        cached_gb = memory.cached / (1024**3)
        shared_gb = memory.shared / (1024**3)
        swap_total_gb = memory.swap_total / (1024**3)
        swap_used_gb = memory.swap_used / (1024**3)

        # Primary stats
        primary_stats_row(
            [
                ("Usage", f"{memory.usage:.1f}%", "text-green-600"),
                ("Used", f"{used_gb:.1f} GB"),
                ("Free", f"{free_gb:.1f} GB"),
            ]
        )

        # Secondary stats
        with ui.row().classes("w-full items-center gap-4 text-xs text-gray-600"):
            ui.label(f"Buffers: {buffers_gb:.1f} GB")
            ui.label(f"Cached: {cached_gb:.1f} GB")
            ui.label(f"Shared: {shared_gb:.1f} GB")
            ui.label(
                f"Swap: {swap_used_gb:.1f} / {swap_total_gb:.1f} GB ({memory.swap_usage:.1f}%)"
            )

        # RAM sticks section
        if memory.ram_sticks:
            self._render_ram_sticks(memory.ram_sticks)

    @staticmethod
    def _render_ram_sticks(ram_sticks: list) -> None:
        """Render physical RAM module information"""
        ui.separator().classes("my-3")
        ui.label("Physical RAM Modules").classes("text-sm font-semibold mb-2")

        for i, ram in enumerate(ram_sticks):
            with ui.row().classes(
                "w-full items-center gap-2 mb-1 text-xs border border-black rounded p-2"
            ):
                ui.label(f"{i + 1}.").classes("w-4 text-gray-500")
                ui.label(f"{ram.size:.0f}GB").classes("font-semibold w-12")
                ui.label(ram.type).classes("w-16")
                ui.label(f"{ram.speed} MT/s").classes("w-20")
                ui.label(ram.locator).classes("w-28 text-gray-600")
                ui.label(ram.manufacturer).classes("flex-1 text-gray-600 truncate")
