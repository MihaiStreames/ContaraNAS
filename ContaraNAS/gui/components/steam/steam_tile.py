from nicegui import ui

from ContaraNAS.gui.components.base import BaseTile
from ContaraNAS.gui.components.steam.steam_library_modal_helper import render_modal_content
from ContaraNAS.gui.components.steam.steam_tile_helper import (
    render_color_legend,
    render_drive_info,
    render_library_header,
    render_progress_section,
)
from ContaraNAS.modules.steam.constants import SORT_BY_SIZE


class SteamTile(BaseTile):
    """Steam-specific module tile implementation"""

    module_type = "steam"

    def __init__(self, view_model, controller):
        super().__init__(view_model, controller)

    def render(self, tile_data: dict):
        """Render Steam-specific stats in the tile"""
        libraries = tile_data.get("libraries", [])

        if not libraries:
            ui.label("No Steam libraries found").classes("text-sm text-gray-500")
            return

        # Library progress bars
        for library in libraries:
            self._render_library_bar(library)

    def _render_library_bar(self, library: dict):
        """Render a segmented progress bar for a single library"""
        with ui.column().classes("w-full mb-3 p-2 border rounded cursor-pointer hover:bg-gray-50").on(
            "click", lambda: self._open_library_modal(library["path"])
        ):
            render_library_header(library["path"], library["game_count"])
            render_progress_section(library)
            render_color_legend(library)
            render_drive_info(library)

    async def _open_library_modal(self, library_path: str):
        """Open modal showing all games in the library"""
        # Fetch games from controller
        games = await self.controller.get_library_games(library_path)

        if not games:
            ui.notify("No games found in this library", type="warning")
            return

        # Create dialog
        with ui.dialog() as dialog, ui.card().classes("w-full max-w-3xl"):
            # State for current sort option
            current_sort = {"value": SORT_BY_SIZE}

            def update_modal_content():
                """Re-render modal content with new sort"""
                content_container.clear()
                with content_container:
                    render_modal_content(
                        games,
                        library_path,
                        current_sort["value"],
                        on_sort_change
                    )

            def on_sort_change(new_sort: str):
                """Handle sort change"""
                current_sort["value"] = new_sort
                update_modal_content()

            # Container for modal content
            content_container = ui.column().classes("w-full")

            # Initial render
            with content_container:
                render_modal_content(games, library_path, SORT_BY_SIZE, on_sort_change)

        dialog.open()
