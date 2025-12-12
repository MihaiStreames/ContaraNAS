from datetime import datetime
from pathlib import Path
from typing import Literal

import msgspec


class SteamGame(msgspec.Struct, gc=False):
    """Steam Game data transfer object"""

    app_id: int
    name: str
    install_dir: str
    library_path: str
    size_on_disk: int = 0
    shader_cache_size: int = 0
    workshop_content_size: int = 0
    last_updated: int = 0
    last_played: int = 0
    build_id: str = ""
    bytes_to_download: int = 0
    bytes_downloaded: int = 0
    state_flags: int = 4  # 4 = fully installed
    installed_depots: dict[str, dict[str, str]] = msgspec.field(default_factory=dict)

    @property
    def install_state(self) -> Literal["installed", "updating", "downloading", "paused", "uninstalled"]:
        """Determine current install state"""
        if self.state_flags == 4:
            if self.bytes_to_download > 0:
                return "updating"
            return "installed"
        if self.state_flags == 1026:
            return "updating"
        if 0 < self.bytes_downloaded < self.bytes_to_download:
            return "downloading"
        if self.bytes_to_download > 0:
            return "paused"

        return "uninstalled"

    @property
    def library_path_obj(self) -> Path:
        """Get library path as Path object"""
        return Path(self.library_path)

    @property
    def manifest_path(self) -> Path:
        """Path to the game's manifest file"""
        return self.library_path_obj / "steamapps" / f"appmanifest_{self.app_id}.acf"

    @property
    def install_path(self) -> Path:
        """Full installation path"""
        return self.library_path_obj / "steamapps" / "common" / self.install_dir

    @property
    def total_size(self) -> int:
        """Total size including shader cache and workshop content"""
        return self.size_on_disk + self.shader_cache_size + self.workshop_content_size

    @property
    def update_size(self) -> int:
        """Size of pending updates"""
        return max(0, self.bytes_to_download - self.bytes_downloaded)

    @property
    def last_played_date(self) -> datetime | None:
        """Convert timestamp to datetime"""
        return datetime.fromtimestamp(self.last_played) if self.last_played > 0 else None

    @property
    def last_updated_date(self) -> datetime | None:
        """Convert timestamp to datetime"""
        return datetime.fromtimestamp(self.last_updated) if self.last_updated > 0 else None

    @property
    def store_url(self) -> str:
        """Steam store page URL"""
        return f"https://store.steampowered.com/app/{self.app_id}/"
