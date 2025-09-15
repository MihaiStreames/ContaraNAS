from pathlib import Path
from typing import List, Optional

from ContaraNAS.core.utils import get_logger

from ..services.parsing_service import SteamParsingService
from ..services.path_service import SteamPathService

logger = get_logger(__name__)


class SteamLibraryService:
    """Service for managing Steam installation and libraries"""

    def __init__(self):
        self.steam_path: Optional[Path] = None
        self.library_paths: List[Path] = []
        self.parsing_service: Optional[SteamParsingService] = None

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

        logger.info(
            f"Steam library service initialized: {len(self.library_paths)} libraries"
        )
        return True

    def get_library_paths(self) -> List[Path]:
        """Get all Steam library paths"""
        return self.library_paths.copy()

    def get_steam_path(self) -> Optional[Path]:
        """Get Steam installation path"""
        return self.steam_path
