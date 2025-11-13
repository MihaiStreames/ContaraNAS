from pathlib import Path

from ContaraNAS.core.utils import get_logger

from .parsing_service import SteamParsingService
from .path_service import SteamPathService


logger = get_logger(__name__)


class SteamLibraryService:
    """Service for managing Steam installation and libraries"""

    def __init__(self):
        self.steam_path: Path | None = None
        self.library_paths: list[Path] = []
        self.parsing_service: SteamParsingService | None = None

    def initialize(self) -> bool:
        """Initialize Steam path and libraries"""
        logger.info("Initializing Steam library service...")

        # Find Steam installation
        self.steam_path = SteamPathService.find_steam_path()
        if not self.steam_path:
            logger.error("Steam installation not found")
            return False

        if not SteamPathService.validate_steam_path(self.steam_path):
            logger.error("Invalid Steam installation")
            return False

        self.parsing_service = SteamParsingService(self.steam_path)

        # Load library paths
        self.library_paths = self.parsing_service.get_library_paths()
        if not self.library_paths:
            logger.error("No Steam libraries found")
            return False

        logger.info(f"Steam library service initialized: {len(self.library_paths)} libraries")
        return True

    def get_library_paths(self) -> list[Path]:
        """Get all Steam library paths"""
        return self.library_paths.copy()

    def get_steam_path(self) -> Path | None:
        """Get Steam installation path"""
        return self.steam_path
