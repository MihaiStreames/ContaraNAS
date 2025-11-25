from datetime import datetime
from enum import Enum
from pathlib import Path

from nicegui import ui

from ContaraNAS.core.utils import get_cache_dir
from ContaraNAS.gui.components.shared import format_bytes
from ContaraNAS.modules.steam.constants import IMAGE_CACHE_DIR


class SortOption(str, Enum):
    """Sort options for game list"""

    SIZE = "size"
    NAME = "name"
    LAST_PLAYED = "last_played"

    @property
    def display_name(self) -> str:
        """Human-readable name for UI"""
        return {
            SortOption.SIZE: "Size",
            SortOption.NAME: "Name",
            SortOption.LAST_PLAYED: "Last Played",
        }[self]


def _get_sort_options() -> dict[str, str]:
    """Get sort options dict for ui.select"""
    return {opt.value: opt.display_name for opt in SortOption}


def _sort_games(games: list[dict], sort_by: SortOption) -> list[dict]:
    """Sort games by the specified criteria"""
    if sort_by == SortOption.SIZE:
        return sorted(games, key=lambda g: g["total_size"], reverse=True)
    if sort_by == SortOption.NAME:
        return sorted(games, key=lambda g: g["name"].lower())
    if sort_by == SortOption.LAST_PLAYED:
        return sorted(
            games,
            key=lambda g: g["last_played"] if g["last_played"] > 0 else 0,
            reverse=True,
        )
    return games


def _format_last_played(timestamp: int) -> str:
    """Format last played timestamp to human-readable relative time"""
    if timestamp == 0:
        return "Never played"

    last_played = datetime.fromtimestamp(timestamp)
    now = datetime.now()
    days = (now - last_played).days

    if days == 0:
        return "Today"
    if days == 1:
        return "Yesterday"
    if days < 7:
        return f"{days} days ago"
    if days < 30:
        weeks = days // 7
        return f"{weeks} week{'s' if weeks > 1 else ''} ago"
    if days < 365:
        months = days // 30
        return f"{months} month{'s' if months > 1 else ''} ago"

    years = days // 365
    return f"{years} year{'s' if years > 1 else ''} ago"


def _get_game_image_path(app_id: int) -> Path | None:
    """Get path to cached game image, or None if not cached"""
    image_path = get_cache_dir() / "steam" / IMAGE_CACHE_DIR / f"{app_id}.jpg"
    return image_path if image_path.exists() else None


class GameRowComponent:
    """Renders a single game row in the list"""

    def render(self, game: dict) -> None:
        """Render a game row with image, info, and size"""
        with ui.row().classes("w-full items-center gap-3 p-2 hover:bg-gray-100 rounded"):
            # Game image
            self._render_image(game["app_id"])

            # Game info (name + last played)
            with ui.column().classes("flex-1 gap-0"):
                ui.label(game["name"]).classes("text-sm font-semibold")
                ui.label(_format_last_played(game["last_played"])).classes("text-xs text-gray-500")

            # Size
            ui.label(format_bytes(game["total_size"])).classes("text-sm font-bold min-w-fit")

    @staticmethod
    def _render_image(app_id: int) -> None:
        """Render game image or placeholder"""
        image_path = _get_game_image_path(app_id)

        if image_path:
            ui.image(str(image_path)).classes("w-24 h-auto rounded")
        else:
            with ui.element("div").classes(
                "w-24 h-12 bg-gray-300 rounded flex items-center justify-center"
            ):
                ui.label("No Image").classes("text-xs text-gray-500")


class GameListModal:
    """Modal component for displaying games in a library"""

    def __init__(self):
        self._game_row = GameRowComponent()
        self._current_sort = SortOption.SIZE
        self._games: list[dict] = []
        self._library_path: str = ""
        self._content_container: ui.column | None = None

    async def open(
        self,
        games: list[dict],
        library_path: str,
    ) -> None:
        """Open the modal with the given games"""
        if not games:
            ui.notify("No games found in this library", type="warning")
            return

        self._games = games
        self._library_path = library_path
        self._current_sort = SortOption.SIZE

        with ui.dialog() as dialog, ui.card().classes("w-full max-w-3xl"):
            self._render_modal_content()

        dialog.open()

    def _render_modal_content(self) -> None:
        """Render the complete modal content"""
        with ui.column().classes("w-full gap-4"):
            # Header with path and sort selector
            self._render_header()

            ui.separator()

            # Games list (in container for updates)
            self._content_container = ui.column().classes("w-full")
            with self._content_container:
                self._render_games_list()

            # Footer
            ui.separator()
            self._render_footer()

    def _render_header(self) -> None:
        """Render modal header with title and sort dropdown"""
        with ui.row().classes("w-full justify-between items-center"):
            ui.label(f"Games in: {self._library_path}").classes("text-lg font-bold")

            with ui.row().classes("gap-2 items-center"):
                ui.label("Sort by:").classes("text-sm")
                ui.select(
                    options=_get_sort_options(),
                    value=self._current_sort.value,
                    on_change=self._on_sort_change,
                ).classes("w-32")

    def _render_games_list(self) -> None:
        """Render the scrollable games list"""
        sorted_games = _sort_games(self._games, self._current_sort)

        with ui.scroll_area().classes("w-full h-96"), ui.column().classes("w-full gap-1"):
            for game in sorted_games:
                self._game_row.render(game)

    def _render_footer(self) -> None:
        """Render modal footer with game count"""
        count = len(self._games)
        ui.label(f"Total: {count} game{'s' if count != 1 else ''}").classes("text-sm text-gray-500")

    def _on_sort_change(self, event) -> None:
        """Handle sort option change"""
        self._current_sort = SortOption(event.value)

        # Re-render games list
        if self._content_container:
            self._content_container.clear()
            with self._content_container:
                self._render_games_list()
