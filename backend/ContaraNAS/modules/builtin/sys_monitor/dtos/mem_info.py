import msgspec


class RAMInfo(msgspec.Struct, gc=False, frozen=True):
    """Data transfer object for RAM stick information"""

    locator: str
    bank_locator: str
    size: float
    type: str
    speed: int
    manufacturer: str
    part_number: str


class MemoryInfo(msgspec.Struct, gc=False, frozen=True):
    """Data transfer object for Memory information"""
    
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
    ram_sticks: tuple[RAMInfo, ...] = ()
