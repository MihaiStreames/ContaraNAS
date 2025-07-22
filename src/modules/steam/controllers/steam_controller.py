from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from src.core.utils import get_logger
from ..dtos.steam_game import SteamGame
from ..services.cache_service import SteamCachingService
from ..services.monitoring_service import SteamMonitoringService
from ..services.parsing_service import SteamParsingService

logger = get_logger(__name__)


class SteamController:
    """Controller orchestrating Steam services"""

    def __init__(self, steam_path: Path):
        self.steam_path = steam_path
        self.games: List[SteamGame] = []

        self.parsing_service = SteamParsingService(steam_path)
        self.caching_service = SteamCachingService()
        self.monitoring_service = SteamMonitoringService(steam_path)

        logger.info(f"SteamController initialized with path: {steam_path}")

    def load_games(self) -> None:
        """Load all games from manifest files in Steam libraries"""
        logger.info("Loading Steam games...")
        start_time = datetime.now()

        libraries = self.parsing_service.get_library_paths()
        if not libraries:
            logger.error("No Steam libraries found")
            return

        self.games = []
        manifest_files = self.monitoring_service.get_manifest_files(libraries)

        for manifest_path in manifest_files:
            library_path = manifest_path.parent.parent
            game = self.parsing_service.create_game_from_manifest(manifest_path, library_path)

            if game:
                self.games.append(game)

        # Update cache for each library
        games_by_lib = self.get_games_by_library()

        for lib_path in libraries:
            games = games_by_lib.get(str(lib_path), [])
            size_breakdown = {
                'games': sum(g.size_on_disk for g in games),
                'updates': sum(g.bytes_to_download for g in games),
                'shader_cache': sum(g.shader_cache_size for g in games),
                'workshop': sum(g.workshop_content_size for g in games)
            }
            manifest_files = [g.manifest_path for g in games]

            self.caching_service.cache_library(
                lib_path, manifest_files, size_breakdown, len(games)
            )

        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"Loaded {len(self.games)} games in {duration:.2f}s")

        self.monitoring_service.reset_state()

    def check_for_changes(self) -> Optional[Dict[str, Any]]:
        """Check for manifest changes using monitoring service"""
        libraries = self.parsing_service.get_library_paths()
        if not self.monitoring_service.check_for_changes(libraries):
            return None

        logger.info("Manifest changes detected")

        # Reload games from manifests
        self.load_games()

        return {
            'timestamp': datetime.now().isoformat(),
            'total_games': len(self.games)
        }

    def get_games_by_library(self) -> Dict[str, List[SteamGame]]:
        """Group games by library path"""
        grouped = {}

        for game in self.games:
            lib_path = str(game.library_path)
            grouped.setdefault(lib_path, []).append(game)

        for games in grouped.values():
            games.sort(key=lambda g: g.name.lower())

        return grouped

    def get_library_stats(self) -> Dict[str, Any]:
        """Get statistics for all libraries and cache them"""
        libs = self.parsing_service.get_library_paths()
        games_by_lib = self.get_games_by_library()

        stats = {
            'total_games': len(self.games),
            'total_size': sum(g.total_size for g in self.games),
            'libraries': []
        }

        for lib_path in libs:
            cache = self.caching_service.load_library_cache(lib_path)
            games = games_by_lib.get(str(lib_path), [])

            if cache and len(games) == cache.get('game_count', 0):
                size_breakdown = cache.get('size_breakdown', {})
            else:
                size_breakdown = {
                    'games': sum(g.size_on_disk for g in games),
                    'updates': sum(g.bytes_to_download for g in games),
                    'shader_cache': sum(g.shader_cache_size for g in games),
                    'workshop': sum(g.workshop_content_size for g in games)
                }

            manifest_files = [g.manifest_path for g in games]

            self.caching_service.cache_library(
                lib_path, manifest_files, size_breakdown, len(games)
            )

            lib_stats = {
                'path': str(lib_path),
                'game_count': len(games),
                'total_size': sum(g.total_size for g in games),
                'size_breakdown': size_breakdown
            }

            stats['libraries'].append(lib_stats)

        return stats

    def get_library_data(self) -> Dict[str, Any]:
        """For each library, parse manifests and return SteamGame DTOs as dicts"""
        games_by_library = self.get_games_by_library()
        stats = self.get_library_stats()

        libs = {}

        for lib_stats in stats['libraries']:
            lib_path = lib_stats['path']
            games = [game.to_dict() for game in games_by_library.get(lib_path, [])]

            libs[lib_path] = {
                **lib_stats,
                'games': games
            }

        return libs
