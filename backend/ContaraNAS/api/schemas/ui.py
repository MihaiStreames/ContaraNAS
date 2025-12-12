from pydantic import BaseModel

from .components import ModalSchema
from .components import TileSchema


class TileUI(BaseModel):
    """Serialized tile component"""

    tile: TileSchema


class ModuleUI(BaseModel):
    """Full UI state for a module"""

    tile: TileSchema | None = None
    modals: list[ModalSchema] = []
