from dataclasses import dataclass, field

from nicegui import ui
import plotly.graph_objects as go


@dataclass
class GraphConfig:
    """Configuration for graph appearance"""

    color: str = "#1976d2"
    height: int = 150
    max_range: float = 100
    min_range: float = 0
    fill_opacity: float = 0.3
    line_width: int = 1
    show_hover: bool = True


@dataclass
class SeriesConfig:
    """Configuration for a single data series in multi-series graphs"""

    name: str
    color: str
    history: list[float] = field(default_factory=list)


def _hex_to_rgba(hex_color: str, opacity: float) -> str:
    """Convert hex color to rgba string"""
    hex_color = hex_color.lstrip("#")
    r, g, b = tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
    return f"rgba({r}, {g}, {b}, {opacity})"


def _create_base_layout(config: GraphConfig) -> dict:
    """Create base Plotly layout configuration"""
    return {
        "height": config.height,
        "margin": {"l": 0, "r": 0, "t": 0, "b": 0},
        "xaxis": {
            "showgrid": False,
            "showticklabels": False,
            "zeroline": False,
            "visible": False,
        },
        "yaxis": {
            "showgrid": False,
            "showticklabels": False,
            "zeroline": False,
            "range": [config.min_range, config.max_range],
            "visible": False,
        },
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "showlegend": False,
        "hovermode": "closest" if config.show_hover else False,
    }


class TimeSeriesGraph:
    """Reusable time series graph component with automatic history management

    Usage::

        graph = TimeSeriesGraph(GraphConfig(color="#1976d2", height=150))
        graph.render()  # Initial render

        # On data update:
        graph.update(new_value)  # Automatically manages history and refreshes
    """

    def __init__(self, config: GraphConfig | None = None, max_points: int = 30):
        self.config = config or GraphConfig()
        self.max_points = max_points
        self._history: list[float] = []
        self._plot: ui.plotly | None = None

    @property
    def history(self) -> list[float]:
        """Read-only access to history data"""
        return self._history.copy()

    def _create_figure(self) -> go.Figure:
        """Create Plotly figure from current state"""
        fillcolor = _hex_to_rgba(self.config.color, self.config.fill_opacity)

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                y=self._history,
                mode="lines",
                fill="tozeroy",
                line={"color": self.config.color, "width": self.config.line_width},
                fillcolor=fillcolor,
                hovertemplate="%{y:.1f}%<extra></extra>" if self.config.show_hover else None,
                name="",
            )
        )

        fig.update_layout(**_create_base_layout(self.config))
        return fig

    def render(self, classes: str = "w-full") -> "TimeSeriesGraph":
        """Render the graph component - Returns self for chaining"""
        self._plot = ui.plotly(self._create_figure()).classes(classes)
        return self

    def update(self, value: float) -> None:
        """Push new value and refresh the graph"""
        self._history.append(value)
        if len(self._history) > self.max_points:
            self._history.pop(0)

        if self._plot:
            self._plot.update_figure(self._create_figure())

    def clear(self) -> None:
        """Clear history and refresh"""
        self._history.clear()
        if self._plot:
            self._plot.update_figure(self._create_figure())


class MultiSeriesGraph:
    """Graph component supporting multiple data series

    Usage::

        graph = MultiSeriesGraph(
            series=[
                SeriesConfig(name="Read", color="#1976d2"),
                SeriesConfig(name="Write", color="#388e3c"),
            ],
            config=GraphConfig(height=100),
        )
        graph.render()
        graph.update({"Read": 50.5, "Write": 30.2})
    """

    def __init__(
        self,
        series: list[SeriesConfig],
        config: GraphConfig | None = None,
        max_points: int = 30,
    ):
        self.series = {s.name: s for s in series}
        self.config = config or GraphConfig()
        self.max_points = max_points
        self._plot: ui.plotly | None = None

    def _create_figure(self) -> go.Figure:
        """Create multi-series Plotly figure"""
        fig = go.Figure()

        for series in self.series.values():
            fillcolor = _hex_to_rgba(series.color, self.config.fill_opacity)
            fig.add_trace(
                go.Scatter(
                    y=series.history,
                    mode="lines",
                    fill="tozeroy",
                    line={"color": series.color, "width": self.config.line_width},
                    fillcolor=fillcolor,
                    name=series.name,
                    hovertemplate=f"{series.name}: %{{y:.1f}}<extra></extra>",
                )
            )

        layout = _create_base_layout(self.config)
        layout["showlegend"] = len(self.series) > 1
        fig.update_layout(**layout)
        return fig

    def render(self, classes: str = "w-full") -> "MultiSeriesGraph":
        """Render the graph component - Returns self for chaining"""
        self._plot = ui.plotly(self._create_figure()).classes(classes)
        return self

    def update(self, values: dict[str, float]) -> None:
        """Update multiple series at once"""
        for name, value in values.items():
            if name in self.series:
                self.series[name].history.append(value)
                if len(self.series[name].history) > self.max_points:
                    self.series[name].history.pop(0)

        if self._plot:
            self._plot.update_figure(self._create_figure())


class PerCoreGraphGrid:
    """Grid of mini graphs for per-core CPU visualization"""

    def __init__(
        self,
        num_cores: int,
        config: GraphConfig | None = None,
        max_points: int = 30,
        max_columns: int = 4,
    ):
        self.num_cores = num_cores
        self.max_columns = max_columns
        self.config = config or GraphConfig(height=50, color="#1976d2")
        self.max_points = max_points
        self._core_histories: dict[int, list[float]] = {i: [] for i in range(num_cores)}
        self._plots: dict[int, ui.plotly] = {}
        self._grid_container: ui.grid | None = None

    def _create_core_figure(self, core_index: int) -> go.Figure:
        """Create figure for a single core"""
        history = self._core_histories[core_index]
        fillcolor = _hex_to_rgba(self.config.color, self.config.fill_opacity)

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                y=history,
                mode="lines",
                fill="tozeroy",
                line={"color": self.config.color, "width": 1},
                fillcolor=fillcolor,
                hovertemplate="%{y:.1f}%<extra></extra>",
            )
        )
        fig.update_layout(**_create_base_layout(self.config))
        return fig

    def render(self) -> "PerCoreGraphGrid":
        """Render the grid of core graphs"""
        cols = min(self.max_columns, self.num_cores)

        with ui.grid(columns=cols).classes("w-full gap-1") as grid:
            self._grid_container = grid

            for i in range(self.num_cores):
                with ui.column().classes("w-full"):
                    # Core label - will be updated with current usage
                    ui.label(f"Core {i}: --%").classes("text-[10px] text-black")
                    self._plots[i] = ui.plotly(self._create_core_figure(i)).classes("w-full")

        return self

    def update(self, usage_per_core: list[float]) -> None:
        """Update all core graphs with new usage values"""
        if self._grid_container is None:
            return

        # We need to rebuild to update labels - this is a limitation
        # In a more sophisticated setup, we'd use ui.refreshable per core
        self._grid_container.clear()

        with self._grid_container:
            cols = min(self.max_columns, self.num_cores)
            # Re-set columns since clear removes styling
            self._grid_container._props["columns"] = cols

            for i, usage in enumerate(usage_per_core):
                # Update history
                self._core_histories[i].append(usage)
                if len(self._core_histories[i]) > self.max_points:
                    self._core_histories[i].pop(0)

                with ui.column().classes("w-full"):
                    ui.label(f"Core {i}: {usage:.0f}%").classes("text-[10px] text-black")
                    self._plots[i] = ui.plotly(self._create_core_figure(i)).classes("w-full")
