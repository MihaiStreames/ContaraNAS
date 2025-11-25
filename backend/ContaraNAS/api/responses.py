from pydantic import BaseModel


class PairResponse(BaseModel):
    """Response containing API token after successful pairing"""

    success: bool
    api_token: str
    message: str


class PairingStatusResponse(BaseModel):
    """Response with current pairing status"""

    is_paired: bool
    locked_out: bool
    lockout_remaining_seconds: int
    active_pairing_expires_in: int | None


class VerifyResponse(BaseModel):
    """Response for token verification"""

    valid: bool


class ModuleInfo(BaseModel):
    """Information about a module"""

    name: str
    display_name: str
    enabled: bool
    initialized: bool


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
