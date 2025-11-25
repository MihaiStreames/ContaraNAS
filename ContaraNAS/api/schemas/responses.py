from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


# ============================================================================
# Base Response Models
# ============================================================================


class BaseResponse(BaseModel):
    """Base response model with common fields"""

    success: bool = True
    message: str | None = None
    timestamp: datetime = Field(default_factory=datetime.now)


class ErrorResponse(BaseResponse):
    """Error response model"""

    success: bool = False
    error: str
    details: dict[str, Any] | None = None


# ============================================================================
# System Monitor Schemas
# ============================================================================


class CPUInfoResponse(BaseModel):
    """CPU information response"""

    name: str
    physical_cores: int
    logical_cores: int
    usage_per_core: list[float]
    total_usage: float
    current_speed_ghz: float
    max_speed_ghz: float
    min_speed_ghz: float
    processes: int
    threads: int
    file_descriptors: int
    uptime: float


class RAMStickResponse(BaseModel):
    """Individual RAM stick information"""

    locator: str
    bank_locator: str
    size: float
    type: str
    speed: int
    manufacturer: str
    part_number: str


class MemoryInfoResponse(BaseModel):
    """Memory information response"""

    total: float
    available: float
    free: float
    used: float
    usage: float
    buffers: float
    cached: float
    shared: float
    swap_total: float
    swap_used: float
    swap_free: float
    swap_usage: float
    ram_sticks: list[RAMStickResponse] = Field(default_factory=list)


class DiskInfoResponse(BaseModel):
    """Disk information response"""

    device: str
    mountpoint: str
    filesystem: str
    total_gb: float
    used_gb: float
    free_gb: float
    usage_percent: float
    read_bytes: int
    write_bytes: int
    read_speed: float
    write_speed: float
    read_time: int
    write_time: int
    io_time: int
    busy_time: float
    model: str
    type: str


class SystemStatsResponse(BaseModel):
    """Complete system statistics response"""

    cpu: CPUInfoResponse | None = None
    memory: MemoryInfoResponse | None = None
    disks: list[DiskInfoResponse] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.now)


# ============================================================================
# Steam Module Schemas
# ============================================================================


class SteamGameResponse(BaseModel):
    """Steam game information response"""

    app_id: int
    name: str
    install_dir: str
    library_path: str
    size_on_disk: int
    shader_cache_size: int
    workshop_content_size: int
    total_size: int
    update_size: int
    install_state: Literal["installed", "updating", "downloading", "paused", "uninstalled"]
    last_updated: int
    last_played: int
    build_id: str
    store_url: str
    installed_depots: dict[str, dict[str, str]] = Field(default_factory=dict)


class SteamLibraryResponse(BaseModel):
    """Steam library information response"""

    path: str
    game_count: int
    total_games_size: int
    total_shader_size: int
    total_workshop_size: int
    total_size: int
    drive_total: int
    drive_free: int
    drive_used: int


class SteamOverviewResponse(BaseModel):
    """Steam module overview response"""

    libraries: list[SteamLibraryResponse] = Field(default_factory=list)
    total_games: int = 0
    total_libraries: int = 0


class SteamLibraryGamesResponse(BaseModel):
    """Response containing games for a specific library"""

    library_path: str
    games: list[SteamGameResponse] = Field(default_factory=list)
    game_count: int = 0


# ============================================================================
# Module Management Schemas
# ============================================================================


class ModuleInfoResponse(BaseModel):
    """Module information response"""

    name: str
    display_name: str
    enabled: bool
    initialized: bool
    state: dict[str, Any] = Field(default_factory=dict)
    tile_data: dict[str, Any] = Field(default_factory=dict)


class ModuleListResponse(BaseModel):
    """List of all modules response"""

    modules: list[ModuleInfoResponse] = Field(default_factory=list)
    total_count: int = 0
    enabled_count: int = 0


class ModuleToggleRequest(BaseModel):
    """Request to enable/disable a module"""

    enabled: bool


class ModuleToggleResponse(BaseResponse):
    """Response after toggling a module"""

    module_name: str
    enabled: bool


# ============================================================================
# WebSocket Message Schemas
# ============================================================================


class WebSocketMessage(BaseModel):
    """Base WebSocket message"""

    type: str
    data: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)


class SystemStatsMessage(WebSocketMessage):
    """WebSocket message for system stats updates"""

    type: str = "system_stats"
    data: dict[str, Any] = Field(default_factory=dict)


class ModuleStateMessage(WebSocketMessage):
    """WebSocket message for module state changes"""

    type: str = "module_state"
    module_name: str
    change_type: str  # 'enabled', 'disabled', 'state_updated'


class ErrorMessage(WebSocketMessage):
    """WebSocket error message"""

    type: str = "error"
    error: str
    code: str | None = None
