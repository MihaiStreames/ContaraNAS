from datetime import datetime

from nicegui import ui

from src.gui.components.base.module_tile import ModuleTile


class SteamTile(ModuleTile):
    """Steam-specific module tile implementation"""

    def _render_stats(self, tile_data: dict):
        """Render Steam-specific stats in the tile"""
        total_games = tile_data.get("total_games", 0)
        library_count = tile_data.get("library_count", 0)
        last_change = tile_data.get("last_change")

        ui.label(f"Games: {total_games}").classes('text-sm')
        ui.label(f"Libraries: {library_count}").classes('text-sm')

        if not self.module.enabled:
            ui.label("Enable to monitor changes").classes('text-xs text-gray-500')
        else:
            ui.label("Monitoring for changes...").classes('text-xs text-green-600')

            # Show last change info if available
            if last_change:
                if isinstance(last_change, str):
                    change_time = datetime.fromisoformat(last_change.replace('Z', '+00:00'))
                else:
                    change_time = last_change

                # Show relative time
                time_diff = datetime.now() - change_time.replace(tzinfo=None)

                if time_diff.total_seconds() < 60:
                    time_str = "Just now"
                elif time_diff.total_seconds() < 3600:
                    minutes = int(time_diff.total_seconds() / 60)
                    time_str = f"{minutes}m ago"
                elif time_diff.total_seconds() < 86400:
                    hours = int(time_diff.total_seconds() / 3600)
                    time_str = f"{hours}h ago"
                else:
                    days = int(time_diff.total_seconds() / 86400)
                    time_str = f"{days}d ago"

                last_change_type = self.module.state.get('last_change_type', '')
                last_change_file = self.module.state.get('last_change_file', '')

                if last_change_type and last_change_file:
                    ui.label(f"Last: {last_change_type} - {time_str}").classes('text-xs text-blue-600')
                else:
                    ui.label(f"Last change: {time_str}").classes('text-xs text-blue-600')
