from dataclasses import dataclass


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
    dirty: float
    writeback: float
