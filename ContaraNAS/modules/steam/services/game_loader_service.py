import asyncio
from pathlib import Path

from ContaraNAS.core.utils import get_logger
from ContaraNAS.modules.steam.constants import (
    APP_MANIFEST_PATTERN,
    SHADERCACHE_DIR,
    STEAMAPPS_DIR,
    WORKSHOP_CONTENT_DIR,
    WORKSHOP_DIR,
)
from ContaraNAS.modules.steam.dtos import SteamGame
from ContaraNAS.modules.steam.services.parsing_service import SteamParsingService
from ContaraNAS.modules.steam.utils import get_dir_size


logger = get_logger(__name__)


class SteamGameLoaderService:
    """Service for loading Steam games with complete size information"""

    def __init__(self, parsing_service: SteamParsingService):
        self.parsing_service: SteamParsingService = parsing_service

    async def load_games_from_library(self, library_path: Path) -> list[SteamGame]:
        """Load all games from a library with complete size information"""
        steamapps_path = library_path / STEAMAPPS_DIR
        games: list[SteamGame] = []

        # Parse all games in this library
        if not steamapps_path.exists():
            logger.warning(f"Steamapps directory not found: {steamapps_path}")
            return games

        for manifest_path in steamapps_path.glob(APP_MANIFEST_PATTERN):
            game = self.parsing_service.create_game_from_manifest(manifest_path, library_path)
            if game:
                games.append(game)

        # Calculate shader and workshop sizes asynchronously for all games in parallel
        if games:
            await self._calculate_additional_sizes(library_path, games)

        return games

    @staticmethod
    async def _calculate_additional_sizes(library_path: Path, games: list[SteamGame]) -> None:
        """Calculate shader and workshop sizes for all games in parallel"""
        size_tasks = []

        for game in games:
            shader_path = library_path / STEAMAPPS_DIR / SHADERCACHE_DIR / str(game.app_id)
            workshop_path = (
                library_path / STEAMAPPS_DIR / WORKSHOP_DIR / WORKSHOP_CONTENT_DIR / str(game.app_id)
            )

            # Create async tasks for size calculations
            shader_task = (
                asyncio.create_task(get_dir_size(shader_path))
                if shader_path.exists()
                else asyncio.create_task(asyncio.sleep(0, 0))
            )

            workshop_task = (
                asyncio.create_task(get_dir_size(workshop_path))
                if workshop_path.exists()
                else asyncio.create_task(asyncio.sleep(0, 0))
            )

            size_tasks.append((game, shader_task, workshop_task))

        # Execute all size calculations in parallel
        for game, shader_task, workshop_task in size_tasks:
            shader_size, workshop_size = await asyncio.gather(shader_task, workshop_task)
            game.shader_cache_size = shader_size or 0
            game.workshop_content_size = workshop_size or 0
