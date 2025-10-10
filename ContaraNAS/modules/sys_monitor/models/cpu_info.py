from dataclasses import dataclass


@dataclass
class CPUInfo:
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
