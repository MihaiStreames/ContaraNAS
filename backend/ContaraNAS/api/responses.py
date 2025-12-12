from typing import Any

from pydantic import BaseModel

from .schemas.components import ModalSchema
from .schemas.components import TileSchema
from .schemas.ui import ModuleUI


class SuccessResponse(BaseModel):
    """Generic success response"""

    success: bool
    message: str


class PairResponse(BaseModel):
    """Response containing API token after successful pairing"""

    success: bool
    api_token: str
    message: str


class ModuleInfo(BaseModel):
    """Information about a module"""

    name: str
    display_name: str
    enabled: bool
    initialized: bool
    source: str
    removable: bool
    version: str
    system_deps: list[str]


class ModuleListResponse(BaseModel):
    """Response listing all modules"""

    modules: list[ModuleInfo]


class ModuleToggleResponse(BaseModel):
    """Response for module enable/disable toggle"""

    success: bool
    module: str
    enabled: bool


class HealthResponse(BaseModel):
    """Health check response"""

    status: str
    timestamp: str
    checks: dict[str, str]


class InfoResponse(BaseModel):
    """Server information response"""

    name: str
    version: str
    timestamp: str


class ModuleUIResponse(BaseModel):
    """Full UI response for a module"""

    module: str
    ui: ModuleUI


class ModuleTileResponse(BaseModel):
    """Tile-only response for a module"""

    module: str
    tile: TileSchema


class ModuleModalsResponse(BaseModel):
    """Modals-only response for a module"""

    module: str
    modals: list[ModalSchema]


class ActionResultItem(BaseModel):
    """Single action result item"""

    type: str
    modal_id: str | None = None
    message: str | None = None
    variant: str | None = None


class ActionResultResponse(BaseModel):
    """Response from invoking an action"""

    success: bool
    module: str
    action: str
    results: list[dict[str, Any]]


class ActionListResponse(BaseModel):
    """List of available actions for a module"""

    module: str
    actions: list[str]


class ModuleSnapshot(BaseModel):
    """Snapshot of a module's current state including UI"""

    name: str
    display_name: str
    enabled: bool
    initialized: bool
    ui: ModuleUI | None = None


class AppStateResponse(BaseModel):
    """Full application state response"""

    modules: list[ModuleSnapshot]
    active_modal: str | None = None
