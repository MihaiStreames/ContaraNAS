import msgspec


class DiskInfo(msgspec.Struct, gc=False, frozen=True):
    """Data transfer object for Disk information"""

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
