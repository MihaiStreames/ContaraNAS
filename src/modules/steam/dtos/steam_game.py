from pathlib import Path
from typing import Optional, Dict

from pydantic import BaseModel, Field, computed_field


class SteamGame(BaseModel):
    """Steam Game Data Transfer Object (DTO)"""

    # Core attributes
    app_id: int = Field(..., description="Steam App ID")
    name: str = Field(..., description="Game name")
    library_path: Path = Field(..., description="Steam library path where game is installed")

    # URLs
    cover_image_url: str = Field(default="", description="URL to game's cover image")
    store_page_url: Optional[str] = Field(default=None, description="Steam store page URL")

    # Size information (in bytes)
    size_on_disk: int = Field(default=0, description="Main game files size")
    dlc_size: int = Field(default=0, description="DLC content size")
    shader_cache_size: int = Field(default=0, description="Shader cache size")
    workshop_content_size: int = Field(default=0, description="Workshop content size")

    # Depot information
    depots: Dict[str, int] = Field(default_factory=dict, description="Depot information (depot_id: size_bytes)")

    class Config:
        # Allow Path objects
        arbitrary_types_allowed = True
        # Enable validation on assignment
        validate_assignment = True

    def __init__(
            self,
            **data
    ):
        super().__init__(**data)

        # Set default cover image URL if not provided
        if not self.cover_image_url:
            self.cover_image_url = f"https://steamcdn-a.akamaihd.net/steam/apps/{self.app_id}/header.jpg"

    @computed_field
    @property
    def manifest_path(
            self
    ) -> Path:
        """Get the path to the game's manifest file"""
        return self.library_path / 'steamapps' / f'appmanifest_{self.app_id}.acf'

    @computed_field
    @property
    def shader_cache_path(
            self
    ) -> Path:
        """Get the path to the game's shader cache directory"""
        return self.library_path / 'steamapps' / 'shadercache' / str(self.app_id)

    @computed_field
    @property
    def workshop_path(
            self
    ) -> Path:
        """Get the path to the game's workshop content directory."""
        return self.library_path / 'steamapps' / 'workshop' / 'content' / str(self.app_id)

    @computed_field
    @property
    def total_size(
            self
    ) -> int:
        """Calculate total game size"""
        return (
                self.size_on_disk +
                self.dlc_size +
                self.shader_cache_size +
                self.workshop_content_size
        )

    def to_dict(
            self
    ) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            "app_id": self.app_id,
            "name": self.name,
            "library_path": str(self.library_path),
            "cover_image_url": self.cover_image_url,
            "store_page_url": self.store_page_url,
            "size_on_disk": self.size_on_disk,
            "dlc_size": self.dlc_size,
            "shader_cache_size": self.shader_cache_size,
            "workshop_content_size": self.workshop_content_size,
            "total_size": self.total_size,
            "depots": self.depots
        }
