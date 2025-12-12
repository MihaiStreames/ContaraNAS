import msgspec


class CPUInfo(msgspec.Struct, gc=False, frozen=True):
    """Data transfer object for CPU information"""

    name: str
    physical_cores: int
    logical_cores: int
    usage_per_core: tuple[float, ...]  # tuple is faster than list for fixed data
    total_usage: float
    current_speed_ghz: float
    max_speed_ghz: float
    min_speed_ghz: float
    processes: int
    threads: int
    file_descriptors: int
    uptime: float
