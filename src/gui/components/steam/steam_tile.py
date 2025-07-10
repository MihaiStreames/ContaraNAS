from nicegui import ui

from src.gui.components.base.module_tile import ModuleTile
from src.gui.utils.gui_utils import format_bytes


class SteamTile(ModuleTile):
    """Steam-specific module tile implementation"""

    def _render_stats(self, tile_data: dict):
        """Render Steam-specific stats in the tile"""
        total_games = tile_data.get("total_games", 0)
        total_size = tile_data.get("total_size", 0)
        libraries = tile_data.get("libraries", {})

        # Basic stats
        ui.label(f"Games: {total_games}").classes('text-sm')
        ui.label(f"Total Size: {format_bytes(total_size)}").classes('text-sm')
        ui.label(f"Libraries: {len(libraries)}").classes('text-sm')

        # Show size breakdown if available
        if total_games > 0:
            with ui.expansion("Size Breakdown").classes('w-full'):
                # Calculate totals for breakdown
                total_game_size = sum(lib.get("size_breakdown", {}).get("games", 0) for lib in libraries.values())
                total_dlc_size = sum(lib.get("size_breakdown", {}).get("dlc", 0) for lib in libraries.values())
                total_shader_size = sum(
                    lib.get("size_breakdown", {}).get("shader_cache", 0) for lib in libraries.values())
                total_workshop_size = sum(
                    lib.get("size_breakdown", {}).get("workshop", 0) for lib in libraries.values())

                ui.label(f"Games: {format_bytes(total_game_size)}").classes('text-xs ml-4')
                ui.label(f"DLC: {format_bytes(total_dlc_size)}").classes('text-xs ml-4')
                ui.label(f"Shader Cache: {format_bytes(total_shader_size)}").classes('text-xs ml-4')
                ui.label(f"Workshop: {format_bytes(total_workshop_size)}").classes('text-xs ml-4')
