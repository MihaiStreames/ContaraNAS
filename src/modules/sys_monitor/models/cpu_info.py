from dataclasses import dataclass
from typing import List, Optional


@dataclass
class CpuInfo:
    name: str
    physical_cores: int
    logical_cores: int
    sockets: int
    usage_per_core: List[float]
    total_usage: float
    current_speed_ghz: float
    max_speed_ghz: float
    min_speed_ghz: float
    processes: int
    threads: int
    file_descriptors: int
    uptime: float
