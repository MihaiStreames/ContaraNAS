from nicegui import ui

from src.gui.components.base.module_dialog import ModuleDialog
from src.gui.utils.gui_utils import format_bytes


class SteamDialog(ModuleDialog):
    """Steam-specific module detail dialog implementation"""

    def _render_details(
            self,
            detailed_data: dict
    ):
        """Render Steam-specific details"""
        total_games = detailed_data.get("total_games", 0)
        libraries = detailed_data.get("libraries", {})

        # Summary
        ui.label(f"Total Games: {total_games}").classes('text-lg font-semibold mb-4')

        if not libraries:
            ui.label("No Steam libraries found").classes('text-gray-500')
            return

        # Libraries section
        ui.label("Steam Libraries").classes('text-md font-semibold mb-2')

        for library_path, library_data in libraries.items():
            with ui.expansion(f"Library: {library_path}").classes('w-full mb-2'):
                game_count = library_data.get("game_count", 0)
                size_breakdown = library_data.get("size_breakdown", {})
                games = library_data.get("games", [])

                # Library summary
                ui.label(f"Games: {game_count}").classes('font-medium')

                # Size breakdown
                with ui.row().classes('gap-4 mb-4'):
                    ui.label(f"Games: {format_bytes(size_breakdown.get('games', 0))}").classes('text-sm')
                    ui.label(f"DLC: {format_bytes(size_breakdown.get('dlc', 0))}").classes('text-sm')
                    ui.label(f"Shader Cache: {format_bytes(size_breakdown.get('shader_cache', 0))}").classes('text-sm')
                    ui.label(f"Workshop: {format_bytes(size_breakdown.get('workshop', 0))}").classes('text-sm')

                ui.label(f"Total: {format_bytes(size_breakdown.get('total', 0))}").classes('font-medium')

                # Games list
                if games:
                    with ui.expansion(f"Games ({len(games)})").classes('w-full'):
                        with ui.column().classes('w-full max-h-64 overflow-auto'):
                            for game in games:
                                with ui.row().classes('w-full justify-between items-center p-2 border-b'):
                                    ui.label(game.get("name", "Unknown Game")).classes('font-medium')
                                    ui.label(format_bytes(game.get("total_size", 0))).classes('text-sm text-gray-600')
