import asyncio
from datetime import datetime
from pathlib import Path

from ContaraNAS.core import get_logger
from ContaraNAS.core import to_builtins
from ContaraNAS.core.action import ActionRef
from ContaraNAS.core.action import Notify
from ContaraNAS.core.action import OpenModal
from ContaraNAS.core.action import action
from ContaraNAS.core.module import Module
from ContaraNAS.core.module import ModuleState
from ContaraNAS.core.ui import Modal
from ContaraNAS.core.ui import Tile

from .services import SteamCacheService
from .services import SteamGameLoaderService
from .services import SteamImageService
from .services import SteamLibraryService
from .services import SteamMonitoringService
from .services import SteamParsingService
from .utils import extract_app_id
from .utils import get_drive_info
from .views import build_library_modal
from .views import build_tile
from .views import get_library_modal_id


logger = get_logger(__name__)


class SteamModule(Module):
    """Module for managing Steam library"""

    class State(ModuleState):
        """Steam module state"""

        initialized_at: datetime | None = None
        steam_available: bool = False
        steam_path: str | None = None
        status: str = "not_initialized"
        last_scan_completed: datetime | None = None
        last_change_at: datetime | None = None
        last_change_type: str | None = None
        last_change_app_id: int | None = None

        # Cached data
        libraries: list[dict] = []
        games: list[dict] = []
        total_games: int = 0
        total_libraries: int = 0
        total_size: int = 0
        error: str | None = None

    def __init__(
        self,
        name: str = "steam",
        display_name: str | None = None,
        metadata=None,
    ) -> None:
        super().__init__(name, display_name or "Steam", metadata)

        # Initialize services
        self._library_service = SteamLibraryService()
        self._cache_service = SteamCacheService()
        self._image_service = SteamImageService()

        # These are initialized only if Steam is found
        self._parsing_service: SteamParsingService | None = None
        self._game_loader_service: SteamGameLoaderService | None = None
        self._monitoring_service: SteamMonitoringService | None = None

        self._event_loop: asyncio.AbstractEventLoop | None = None
        self._monitor_flag = False

    @property
    def state(self) -> "SteamModule.State":
        """Type-safe state accessor"""
        assert self._typed_state is not None
        return self._typed_state

    async def _analyze_library(self, library_path: Path) -> tuple[dict, list[dict]]:
        """Analyze a single library and return summary info with games list"""
        games = await self._game_loader_service.load_games_from_library(library_path)

        total_games_size = sum(game.size_on_disk for game in games)
        total_shader_size = sum(game.shader_cache_size for game in games)
        total_workshop_size = sum(game.workshop_content_size for game in games)
        total_size = total_games_size + total_shader_size + total_workshop_size

        drive_info = get_drive_info(library_path)

        library_summary = {
            "path": str(library_path),
            "game_count": len(games),
            "total_games_size": total_games_size,
            "total_shader_size": total_shader_size,
            "total_workshop_size": total_workshop_size,
            "total_size": total_size,
            "drive_total": drive_info["total"],
            "drive_free": drive_info["free"],
            "drive_used": drive_info["used"],
        }

        games_data = [to_builtins(game) for game in games]
        return library_summary, games_data

    async def _load_data(self) -> None:
        """Load all Steam data into state"""
        if not self.state.steam_available:
            return

        try:
            libraries_data = []
            all_games = []

            for library_path in self._library_service.get_library_paths():
                library_info, games = await self._analyze_library(library_path)
                libraries_data.append(library_info)
                all_games.extend(games)

            total_size = sum(lib.get("total_size", 0) for lib in libraries_data)

            self.state.libraries = libraries_data
            self.state.games = all_games
            self.state.total_games = len(all_games)
            self.state.total_libraries = len(libraries_data)
            self.state.total_size = total_size
            self.state.error = None

        except Exception as e:
            logger.error(f"Error loading Steam data: {e}")
            self.state.error = str(e)

    async def _on_manifest_change(self, event_type: str, app_id: int) -> None:
        """Handle manifest change - update state and reload data"""
        self.state.last_change_at = datetime.now()
        self.state.last_change_type = event_type
        self.state.last_change_app_id = app_id

        # Reload data to reflect changes
        await self._load_data()
        self.state.commit()

    def _handle_manifest_change(self, event_type: str, manifest_path: Path) -> None:
        """Handle manifest file changes from the monitoring service"""
        if not self.state.steam_available:
            return

        app_id_str = extract_app_id(manifest_path)
        if not app_id_str:
            return

        app_id = int(app_id_str)
        logger.info(f"Steam app {app_id} {event_type}: {manifest_path.name}")

        cache_action = None

        if event_type == "deleted":
            if self._cache_service.remove_manifest(manifest_path):
                cache_action = "removed"
                self._image_service.remove_image(app_id)

        elif event_type in ["created", "modified"]:
            action = self._cache_service.update_manifest(manifest_path)

            if action != "no_change":
                cache_action = action

                if action == "added" and self._event_loop:
                    asyncio.run_coroutine_threadsafe(
                        self._image_service.download_image(app_id),
                        self._event_loop,
                    )

        if cache_action and self._event_loop:
            asyncio.run_coroutine_threadsafe(
                self._on_manifest_change(event_type, app_id),
                self._event_loop,
            )

    async def initialize(self) -> None:
        """Initialize the Steam module"""
        logger.info("Initializing Steam module...")

        # Capture event loop for thread callbacks
        self._event_loop = asyncio.get_running_loop()

        # Initialize library service to find Steam
        if not self._library_service.initialize():
            logger.warning("Steam not found on this system")
            self.state.initialized_at = datetime.now()
            self.state.steam_available = False
            self.state.status = "steam_not_found"
            self.state.commit()
            return

        steam_path = self._library_service.get_steam_path()
        logger.debug(f"Steam found at: {steam_path}")

        # Initialize services that require Steam
        self._parsing_service = SteamParsingService(steam_path)
        self._game_loader_service = SteamGameLoaderService(self._parsing_service)
        self._monitoring_service = SteamMonitoringService(self._handle_manifest_change)

        # Initialize caches
        library_paths = self._library_service.get_library_paths()
        self._cache_service.initialize_cache(library_paths)

        # Sync image cache
        installed_app_ids = self._cache_service.get_installed_app_ids()
        await self._image_service.sync_with_manifest_cache(installed_app_ids)

        # Update state
        self.state.initialized_at = datetime.now()
        self.state.steam_available = True
        self.state.steam_path = str(steam_path)
        self.state.status = "ready"
        self.state.last_scan_completed = datetime.now()

        # Load initial data
        await self._load_data()

        self.state.commit()
        logger.info("Steam module initialized successfully")

    async def start_monitoring(self) -> None:
        """Start Steam library monitoring"""
        if not self.state.steam_available:
            logger.debug("Steam not available, skipping monitoring")
            return

        if self._monitor_flag:
            logger.debug("Monitoring already started")
            return

        self._cache_service.update_cache(self._library_service.get_library_paths())
        self._monitoring_service.start_monitoring(self._library_service.get_library_paths())
        self._monitor_flag = True
        logger.info("Steam monitoring started")

    async def stop_monitoring(self) -> None:
        """Stop Steam library monitoring"""
        if not self._monitor_flag:
            logger.debug("Monitoring already stopped")
            return

        if self._monitoring_service:
            self._monitoring_service.stop_monitoring()

        self._monitor_flag = False

        await self._image_service.cleanup()
        logger.info("Steam monitoring stopped")

    def _get_library_open_actions(self) -> dict:
        """Build a map of library paths to their ActionRef objects"""
        actions = {}
        for lib in self.state.libraries:
            path = lib.get("path", "")

            if path:
                actions[path] = ActionRef(self.open_library, library_path=path)

        return actions

    def get_tile(self) -> Tile:
        """Return the dashboard tile UI component"""
        return build_tile(
            status=self.state.status,
            total_games=self.state.total_games,
            total_libraries=self.state.total_libraries,
            total_size=self.state.total_size,
            libraries=self.state.libraries,
            open_library_actions=self._get_library_open_actions(),
        )

    def get_modals(self) -> list[Modal]:
        """Return modal definitions for this module (one per library)"""
        return [build_library_modal(lib, self.state.games) for lib in self.state.libraries]

    @action
    async def refresh(self) -> Notify:
        """Manually refresh Steam data"""
        if not self.state.steam_available:
            return Notify(message="Steam is not available", variant="warning")

        await self._load_data()
        return Notify(message="Steam data refreshed", variant="success")

    @action
    async def open_library(self, library_path: str) -> OpenModal:
        """Open the modal for a specific library"""
        await self._load_data()
        modal_id = get_library_modal_id(library_path)
        return OpenModal(modal_id=modal_id)
