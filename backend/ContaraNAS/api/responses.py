from pydantic import BaseModel


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


class ModuleActionResponse(BaseModel):
    """Response for module enable/disable actions"""

    success: bool
    module: str
    enabled: bool


class HealthResponse(BaseModel):
    """Health check response"""

    status: str
    timestamp: str


class InfoResponse(BaseModel):
    """Server information response"""

    name: str
    version: str
    timestamp: str
