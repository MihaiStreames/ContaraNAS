from pathlib import Path
from typing import Optional, Dict

from pydantic import BaseModel, Field, computed_field


class SteamGame(BaseModel):
    """Steam Game DTO"""

    # Attributes
    app_id: int
    name: str
    library_path: Path
    cover_image_url: str = ""
    store_page_url: Optional[str] = None

    # Sizes
    size_on_disk: int = Field(default=0, description="Game files")
    dlc_size: int = Field(default=0, description="DLC content")
    shader_cache_size: int = Field(default=0, description="Shader cache")
    workshop_content_size: int = Field(default=0, description="Workshop content")

    # Depots
    depots: Dict[str, str] = Field(default_factory=dict)

    class Config:
        # Allow Path objects
        arbitrary_types_allowed = True

    def __init__(self, **data):
        super().__init__(**data)
        self.manifest_path = self.library_path / 'steamapps' / str('appmanifest_' + str(self.app_id) + '.acf')

    @computed_field
    @property
    def total_size(self) -> int:
        """Calculate total game size"""
        return (
                self.size_on_disk +
                self.dlc_size +
                self.shader_cache_size +
                self.workshop_content_size
        )
