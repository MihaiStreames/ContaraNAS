from dataclasses import dataclass, field


@dataclass
class RAMInfo:
    locator: str
    bank_locator: str
    size: float
    type: str
    speed: int
    manufacturer: str
    part_number: str


@dataclass
class MemoryInfo:
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
    ram_sticks: list[RAMInfo] = field(default_factory=list)
