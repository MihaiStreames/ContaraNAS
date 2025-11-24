from pathlib import Path
import platform
import time
from typing import Any

import psutil

from ContaraNAS.modules.sys_monitor.dtos import CPUInfo

from .hardware_cache_service import HardwareCacheService


class CPUService:
    """Service to monitor CPU information and usage"""

    def __init__(self, os_name: str | None = None):
        self._os_name: str = os_name or platform.system()
        self._hardware_cache = HardwareCacheService()

        self._cpu_static_info: dict | None = None

    def _collect_cpu_hardware_info(self) -> dict[str, Any]:
        """Collect static CPU hardware info"""
        name = self._get_cpu_name()
        physical_cores = psutil.cpu_count(logical=False) or 0
        logical_cores = psutil.cpu_count(logical=True) or 0

        # Get frequency ranges
        freq = psutil.cpu_freq()
        max_speed_ghz = freq.max / 1000 if freq and freq.max else 0
        min_speed_ghz = freq.min / 1000 if freq and freq.min else 0

        return {
            "name": name,
            "physical_cores": physical_cores,
            "logical_cores": logical_cores,
            "max_speed_ghz": max_speed_ghz,
            "min_speed_ghz": min_speed_ghz,
        }

    def _get_cpu_name(self) -> str:
        """Get CPU name based on OS"""
        if self._os_name == "Windows":
            return platform.processor()
        if self._os_name == "Linux":
            try:
                with Path("/proc/cpuinfo").open() as f:
                    for line in f:
                        if "model name" in line:
                            return str(line.split(":", 1)[1].strip())
                return "Unknown"
            except FileNotFoundError:
                return "Unknown"
        return "Unknown"

    def _load_cpu_static_info(self) -> dict[str, Any]:
        """Load CPU static info from cache or collect it"""
        if self._cpu_static_info is None:
            # CPU info never changes, so we can cache it indefinitely
            # Use boot_time-based cache but it's effectively permanent
            self._cpu_static_info = self._hardware_cache.get_or_collect_hardware_info(
                self._collect_cpu_hardware_info
            )
        return self._cpu_static_info

    def get_cpu_info(self) -> CPUInfo:
        """Get comprehensive CPU information and usage stats"""
        # Load static info from cache
        static_info = self._load_cpu_static_info()

        # Collect dynamic info
        usage_per_core = psutil.cpu_percent(interval=None, percpu=True)
        total_usage = psutil.cpu_percent(interval=None)
        current_freq = psutil.cpu_freq()
        current_speed_ghz = current_freq.current / 1000 if current_freq else 0

        processes = len(psutil.pids())
        threads = sum(p.num_threads() for p in psutil.process_iter())
        file_descriptors = psutil.Process().num_fds() if hasattr(psutil.Process(), "num_fds") else 0
        uptime = time.time() - psutil.boot_time()

        return CPUInfo(
            name=static_info["name"],
            physical_cores=static_info["physical_cores"],
            logical_cores=static_info["logical_cores"],
            usage_per_core=usage_per_core,
            total_usage=total_usage,
            current_speed_ghz=current_speed_ghz,
            max_speed_ghz=static_info["max_speed_ghz"],
            min_speed_ghz=static_info["min_speed_ghz"],
            processes=processes,
            threads=threads,
            file_descriptors=file_descriptors,
            uptime=uptime,
        )
