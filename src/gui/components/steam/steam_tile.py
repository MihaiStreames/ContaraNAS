from nicegui import ui

from src.core.event_bus import event_bus
from src.gui.components.base.module_tile import ModuleTile
from src.gui.utils.gui_utils import format_relative_time


class SteamTile(ModuleTile):
    """Steam-specific module tile implementation"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._setup_event_listeners()

    def _setup_event_listeners(self):
        """Set up event listeners for real-time updates"""
        event_bus.subscribe(f'module.{self.name}.state_changed', self.update_state)

    def update_state(self, event_data=None):
        """Update the tile's state"""
        super().update_state(event_data)

    def render(self, tile_data: dict):
        """Render Steam-specific stats in the tile"""
        total_games = tile_data.get("total_games", 0)
        library_count = tile_data.get("library_count", 0)
        last_change = tile_data.get("last_change")

        ui.label(f"Games: {total_games}").classes('text-sm')
        ui.label(f"Libraries: {library_count}").classes('text-sm')

        if not self.module.enable_flag:
            ui.label("Enable to monitor changes").classes('text-xs text-gray-500')
        else:
            ui.label("Monitoring for changes...").classes('text-xs text-green-600')

            # Show last change info if available
            if last_change:
                time_str = format_relative_time(last_change)

                last_change_type = self.module.state.get('last_change_type', '')
                last_change_file = self.module.state.get('last_change_file', '')
                last_change_app_id = self.module.state.get('last_change_app_id', '')

                if last_change_type and last_change_app_id:
                    ui.label(f"Last: {last_change_type} App {last_change_app_id} - {time_str}").classes(
                        'text-xs text-blue-600')
                elif last_change_type and last_change_file:
                    ui.label(f"Last: {last_change_type} {last_change_file} - {time_str}").classes(
                        'text-xs text-blue-600')
                else:
                    ui.label(f"Last change: {time_str}").classes('text-xs text-blue-600')
            else:
                ui.label("No recent changes").classes('text-xs text-gray-500')
