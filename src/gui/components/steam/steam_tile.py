from nicegui import ui

from src.gui.components.base.base_tile import BaseTile


class SteamTile(BaseTile):
    """Steam-specific module tile implementation"""

    def render(self, tile_data: dict):
        """Render Steam-specific stats in the tile"""
        total_games = tile_data.get("total_games", 0)
        library_count = tile_data.get("library_count", 0)

        ui.label(f"Games: {total_games}").classes('text-sm')
        ui.label(f"Libraries: {library_count}").classes('text-sm')

        if not self.view_model.enabled:
            ui.label("Enable to monitor changes").classes('text-xs text-gray-500')
        else:
            ui.label("Monitoring for changes...").classes('text-xs text-green-600')
