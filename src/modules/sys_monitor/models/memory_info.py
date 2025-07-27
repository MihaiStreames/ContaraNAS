from dataclasses import dataclass
from typing import Optional


@dataclass
class MemoryInfo:
    total_gb: float
    available_gb: float
    free_gb: float
    used_gb: float
    usage_percent: float
    buffers_gb: float
    cached_gb: float
    shared_gb: float
    swap_total_gb: float
    swap_used_gb: float
    swap_free_gb: float
    swap_usage_percent: float
    dirty_gb: float
    writeback_gb: float
    speed_mhz: Optional[str] = None
    slots_used: Optional[str] = None
    memory_blocks: Optional[int] = None
    page_size_kb: Optional[int] = None
