from nicegui import ui

from src.gui.components.base.base_tile import BaseTile

from .steam_tile_helper import (render_color_legend, render_drive_info,
                                render_library_header, render_progress_section)


class SteamTile(BaseTile):
    """Steam-specific module tile implementation"""

    def render(self, tile_data: dict):
        """Render Steam-specific stats in the tile"""
        libraries = tile_data.get("libraries", [])

        if not libraries:
            ui.label("No Steam libraries found").classes("text-sm text-gray-500")
            return

        # Library progress bars
        for library in libraries:
            self._render_library_bar(library)

    @staticmethod
    def _render_library_bar(library: dict):
        """Render a segmented progress bar for a single library"""
        with ui.column().classes("w-full mb-3 p-2 border rounded"):
            render_library_header(library["path"], library["game_count"])
            render_progress_section(library)
            render_color_legend(library)
            render_drive_info(library)
