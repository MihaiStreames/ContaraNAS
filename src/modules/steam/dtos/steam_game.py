from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Literal

from pydantic import BaseModel, Field, computed_field

from src.modules.steam.utils.steam_helpers import get_size


class SteamGame(BaseModel):
    """Steam Game Data Transfer Object (DTO)"""

    # Core identifiers
    app_id: int = Field(..., description="Steam App ID")
    name: str = Field(..., description="Game name")
    install_dir: str = Field(..., description="Installation directory name")

    # Paths
    library_path: Path = Field(..., description="Steam library path")

    # Size information
    size_on_disk: int = Field(default=0, description="Size on disk in bytes")

    # Timestamps
    last_updated: int = Field(default=0, description="Last update timestamp")
    last_played: int = Field(default=0, description="Last played timestamp")

    # Build info
    build_id: str = Field(default="", description="Current build ID")

    # Update status
    bytes_to_download: int = Field(default=0, description="Bytes still to download")
    bytes_downloaded: int = Field(default=0, description="Bytes already downloaded")

    # Install state
    state_flags: int = Field(default=4, description="State flags from manifest")  # 4 = fully installed

    # Installed depots
    installed_depots: Dict[str, Dict[str, str]] = Field(default_factory=dict)

    class Config:
        arbitrary_types_allowed = True

    @computed_field
    @property
    def install_state(self) -> Literal['installed', 'updating', 'downloading', 'paused', 'uninstalled']:
        """Determine current install state"""
        if self.state_flags == 4:  # StateFlags "4" = fully installed
            if self.bytes_to_download > 0:
                return 'updating'
            return 'installed'
        elif self.state_flags == 1026:  # Update required
            return 'updating'
        elif 0 < self.bytes_downloaded < self.bytes_to_download:
            return 'downloading'
        elif self.bytes_to_download > 0:
            return 'paused'
        else:
            return 'uninstalled'

    @computed_field
    @property
    def manifest_path(self) -> Path:
        """Path to the game's manifest file"""
        return self.library_path / 'steamapps' / f'appmanifest_{self.app_id}.acf'

    @computed_field
    @property
    def install_path(self) -> Path:
        """Full installation path"""
        return self.library_path / 'steamapps' / 'common' / self.install_dir

    @computed_field
    @property
    def total_size(self) -> int:
        """Total size including shader cache and workshop content"""
        return self.size_on_disk + self.shader_cache_size + self.workshop_content_size

    @computed_field
    @property
    def update_size(self) -> int:
        """Size of pending updates"""
        return max(0, self.bytes_to_download - self.bytes_downloaded)

    @computed_field
    @property
    def last_updated_date(self) -> Optional[datetime]:
        """Convert timestamp to datetime"""
        return datetime.fromtimestamp(self.last_updated) if self.last_updated > 0 else None

    @computed_field
    @property
    def last_played_date(self) -> Optional[datetime]:
        """Convert timestamp to datetime"""
        return datetime.fromtimestamp(self.last_played) if self.last_played > 0 else None

    @computed_field
    @property
    def store_url(self) -> str:
        """Steam store page URL"""
        return f"https://store.steampowered.com/app/{self.app_id}/"

    @computed_field
    @property
    def cover_url(self) -> str:
        """Cover image URL"""
        return f"https://steamcdn-a.akamaihd.net/steam/apps/{self.app_id}/header.jpg"

    @computed_field
    @property
    def shader_cache_size(self) -> int:
        """Calculate shader cache size"""
        shader_path = self.library_path / 'steamapps' / 'shadercache' / str(self.app_id)
        return get_size(shader_path) if shader_path.exists() else 0

    @computed_field
    @property
    def workshop_content_size(self) -> int:
        """Calculate workshop content size"""
        workshop_path = self.library_path / 'steamapps' / 'workshop' / 'content' / str(self.app_id)
        return get_size(workshop_path) if workshop_path.exists() else 0

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            "app_id": self.app_id,
            "name": self.name,
            "install_dir": self.install_dir,
            "library_path": str(self.library_path),
            "size_on_disk": self.size_on_disk,
            "shader_cache_size": self.shader_cache_size,
            "workshop_content_size": self.workshop_content_size,
            "total_size": self.total_size,
            "update_size": self.update_size,
            "install_state": self.install_state,
            "last_updated": self.last_updated,
            "last_played": self.last_played,
            "build_id": self.build_id,
            "is_updating": self.is_updating,
            "store_url": self.store_url,
            "cover_url": self.cover_url,
            "installed_depots": self.installed_depots
        }
