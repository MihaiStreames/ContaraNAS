import os
from pathlib import Path
import platform

from ContaraNAS.core.utils import get_logger


logger = get_logger(__name__)


class SteamPathService:
    """Service for detecting Steam installation path"""

    @staticmethod
    def find_steam_path() -> Path | None:
        """Find Steam installation path based on the platform"""
        system = platform.system()

        if system == "Windows":
            paths = [
                r"C:\Program Files (x86)\Steam",
                r"C:\Program Files\Steam",
                os.path.expandvars(r"%ProgramFiles(x86)%\Steam"),
                os.path.expandvars(r"%ProgramFiles%\Steam"),
            ]
        elif system == "Linux":
            paths = [
                Path.expanduser(Path("~/.steam/steam")),
                Path.expanduser(Path("~/.local/share/Steam")),
                "/usr/share/steam",
            ]
        else:
            logger.warning(f"Unknown platform: {system}")
            return None

        # Check each path
        for path_str in paths:
            path = Path(path_str)
            if path.exists() and (path / "steamapps").exists():
                logger.info(f"Found Steam installation at: {path}")
                return path

        logger.error("Steam installation not found")
        return None

    @staticmethod
    def validate_steam_path(steam_path: Path) -> bool:
        """Validate that a path is a valid Steam installation"""
        required_items = [
            steam_path / "steamapps",
            steam_path / "steamapps" / "libraryfolders.vdf",
        ]

        for item in required_items:
            if not item.exists():
                logger.error(f"Required Steam component missing: {item}")
                return False

        return True
