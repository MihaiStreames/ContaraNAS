from dataclasses import dataclass
from typing import List

from .cpu_info import CpuInfo
from .disk_info import DiskInfo
from .memory_info import MemoryInfo
from .network_info import NetworkInfo


@dataclass
class SystemMetrics:
    cpu: CpuInfo
    ram: MemoryInfo
    disks: List[DiskInfo]
    network: NetworkInfo
    timestamp: str
