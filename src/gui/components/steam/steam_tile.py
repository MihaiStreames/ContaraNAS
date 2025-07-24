from nicegui import ui

from src.core.event_bus import event_bus
from src.gui.components.base.module_tile import ModuleTile


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

        ui.label(f"Games: {total_games}").classes('text-sm')
        ui.label(f"Libraries: {library_count}").classes('text-sm')

        if not self.module.enable_flag:
            ui.label("Enable to monitor changes").classes('text-xs text-gray-500')
        else:
            ui.label("Monitoring for changes...").classes('text-xs text-green-600')
