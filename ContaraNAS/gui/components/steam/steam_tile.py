from nicegui import ui

from ContaraNAS.gui.components.base import BaseTile, BaseTileViewModel
from ContaraNAS.gui.components.steam.sub_components import GameListModal, LibraryBarComponent


class SteamTile(BaseTile):
    """Steam library tile showing library breakdown and game counts"""

    module_type = "steam"

    def __init__(self, view_model: BaseTileViewModel, controller):
        # Sub-components
        self._library_bar = LibraryBarComponent()
        self._game_modal = GameListModal()

        super().__init__(view_model, controller)

    def render(self, tile_data: dict) -> None:
        """Render Steam library bars"""
        libraries = tile_data.get("libraries", [])

        if not libraries:
            ui.label("No Steam libraries found").classes("text-sm text-gray-500")
            return

        for library in libraries:
            self._library_bar.render(
                library,
                on_click=lambda path=library["path"]: self._open_library_modal(path),
            )

    async def _open_library_modal(self, library_path: str) -> None:
        """Open modal showing all games in the library"""
        # Get Steam controller from dashboard controller
        steam_controller = self.controller.get_module_controller("steam")

        if not steam_controller:
            ui.notify("Steam module not available", type="negative")
            return

        # Fetch games
        games = await steam_controller.get_library_games(library_path)

        # Open modal
        await self._game_modal.open(games, library_path)
