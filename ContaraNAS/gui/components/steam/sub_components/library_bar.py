from collections.abc import Callable
from dataclasses import dataclass

from nicegui import ui

from ContaraNAS.gui.components.shared import (
    ProgressSegment,
    clickable_section,
    color_legend,
    format_bytes,
    segmented_progress_bar,
)


# Color constants for consistent styling
COLORS = {
    "games": "#1976d2",  # Blue
    "shaders": "#388e3c",  # Green
    "workshop": "#f57c00",  # Orange
    "non_steam": "#fdd835",  # Yellow
}


@dataclass
class LibraryStats:
    """Computed statistics for a Steam library"""

    path: str
    game_count: int
    total_size: int
    games_size: int
    shader_size: int
    workshop_size: int
    non_steam_size: int
    drive_total: int
    drive_free: int
    drive_used: int

    # Percentages (of total drive)
    games_percent: float = 0.0
    shaders_percent: float = 0.0
    workshop_percent: float = 0.0
    non_steam_percent: float = 0.0
    free_percent: float = 0.0

    @classmethod
    def from_library_data(cls, library: dict) -> "LibraryStats":
        """Create LibraryStats from raw library data dict"""
        games_size = library["total_games_size"]
        shader_size = library["total_shader_size"]
        workshop_size = library["total_workshop_size"]
        total_steam_size = library["total_size"]
        drive_total = library["drive_total"]
        drive_used = library["drive_used"]
        drive_free = library["drive_free"]

        # Calculate non-Steam files
        non_steam_size = max(0, drive_used - total_steam_size)

        # Calculate percentages
        if drive_total > 0:
            games_percent = (games_size / drive_total) * 100
            shaders_percent = (shader_size / drive_total) * 100
            workshop_percent = (workshop_size / drive_total) * 100
            non_steam_percent = (non_steam_size / drive_total) * 100
            free_percent = (drive_free / drive_total) * 100
        else:
            games_percent = shaders_percent = workshop_percent = 0.0
            non_steam_percent = free_percent = 0.0

        return cls(
            path=library["path"],
            game_count=library["game_count"],
            total_size=total_steam_size,
            games_size=games_size,
            shader_size=shader_size,
            workshop_size=workshop_size,
            non_steam_size=non_steam_size,
            drive_total=drive_total,
            drive_free=drive_free,
            drive_used=drive_used,
            games_percent=games_percent,
            shaders_percent=shaders_percent,
            workshop_percent=workshop_percent,
            non_steam_percent=non_steam_percent,
            free_percent=free_percent,
        )


class LibraryBarComponent:
    """Renders a Steam library as a clickable segmented progress bar"""

    def render(
        self,
        library: dict,
        on_click: Callable | None = None,
    ) -> None:
        """Render the library bar"""
        stats = LibraryStats.from_library_data(library)

        if on_click:
            with clickable_section(on_click):
                self._render_content(stats)
        else:
            with ui.column().classes("w-full mb-3 p-2 border rounded"):
                self._render_content(stats)

    def _render_content(self, stats: LibraryStats) -> None:
        """Render the internal content of the library bar"""
        # Header
        self._render_header(stats)

        # Progress bar
        self._render_progress_bar(stats)

        # Legend
        self._render_legend(stats)

        # Drive info
        self._render_drive_info(stats)

    @staticmethod
    def _render_header(stats: LibraryStats) -> None:
        """Render library path and game count"""
        with ui.row().classes("w-full justify-between items-center mb-1"):
            ui.label(stats.path).classes("text-xs font-mono text-gray-600")
            ui.label(f"{stats.game_count} games").classes("text-xs font-bold")

    @staticmethod
    def _render_progress_bar(stats: LibraryStats) -> None:
        """Render the segmented progress bar with total size label"""
        if stats.drive_total == 0:
            return

        segments = [
            ProgressSegment(
                value=stats.games_percent,
                color=COLORS["games"],
                label="Games",
                tooltip=f"Games: {format_bytes(stats.games_size)}",
            ),
            ProgressSegment(
                value=stats.shaders_percent,
                color=COLORS["shaders"],
                label="Shaders",
                tooltip=f"Shaders: {format_bytes(stats.shader_size)}",
            ),
            ProgressSegment(
                value=stats.workshop_percent,
                color=COLORS["workshop"],
                label="Workshop",
                tooltip=f"Workshop: {format_bytes(stats.workshop_size)}",
            ),
        ]

        # Only show non-Steam if there's any
        if stats.non_steam_size > 0:
            segments.append(
                ProgressSegment(
                    value=stats.non_steam_percent,
                    color=COLORS["non_steam"],
                    label="Other",
                    tooltip=f"Non-Steam files: {format_bytes(stats.non_steam_size)}",
                )
            )

        with ui.row().classes("w-full items-center gap-2"):
            segmented_progress_bar(segments).classes("flex-1")
            ui.label(format_bytes(stats.total_size)).classes("text-xs font-bold min-w-fit")

    @staticmethod
    def _render_legend(stats: LibraryStats) -> None:
        """Render the color legend"""
        legend_items = [
            (COLORS["games"], "Games", format_bytes(stats.games_size)),
            (COLORS["shaders"], "Shaders", format_bytes(stats.shader_size)),
            (COLORS["workshop"], "Workshop", format_bytes(stats.workshop_size)),
        ]

        if stats.non_steam_size > 0:
            legend_items.append((COLORS["non_steam"], "Other", format_bytes(stats.non_steam_size)))

        color_legend(legend_items)

    @staticmethod
    def _render_drive_info(stats: LibraryStats) -> None:
        """Render drive free space information"""
        if stats.drive_total > 0:
            ui.label(
                f"Drive: {format_bytes(stats.drive_free)} free ({stats.free_percent:.1f}%)"
            ).classes("text-xs text-gray-500")
