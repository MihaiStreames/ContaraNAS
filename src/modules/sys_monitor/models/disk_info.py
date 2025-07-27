from dataclasses import dataclass
from typing import Union


@dataclass
class DiskInfo:
    device: str
    mountpoint: str
    filesystem: str
    total_gb: float
    used_gb: float
    free_gb: float
    usage_percent: float
    read_bytes: Union[int, str]
    write_bytes: Union[int, str]
    read_speed_mb: Union[float, str]
    write_speed_mb: Union[float, str]
    read_time_ms: Union[int, str]
    write_time_ms: Union[int, str]
    io_time_ms: Union[int, str]
    busy_time_percent: Union[float, str]
    model: str = "Unknown"
    type: str = "Unknown"
    size_gb: float = 0.0
