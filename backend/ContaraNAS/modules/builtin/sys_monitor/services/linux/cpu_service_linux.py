from pathlib import Path
import time
from typing import Any

import psutil

from ContaraNAS.core import get_logger
from ContaraNAS.modules.builtin.sys_monitor.dtos import CPUInfo
from ContaraNAS.modules.builtin.sys_monitor.services import CPUService, HardwareCacheService


logger = get_logger(__name__)


class CPUServiceLinux(CPUService):
    """Linux-specific CPU monitoring implementation"""

    def __init__(self):
        self._hardware_cache = HardwareCacheService(cache_name="cpu")
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

    @staticmethod
    def _get_cpu_name() -> str:
        """Get CPU name from /proc/cpuinfo"""
        try:
            with Path("/proc/cpuinfo").open() as f:
                for line in f:
                    if "model name" in line:
                        return str(line.split(":", 1)[1].strip())
            return "Unknown"
        except FileNotFoundError:
            return "Unknown"

    def _load_static_cpu_info(self) -> None:
        """Load CPU static info from cache or collect it"""
        if self._cpu_static_info is None:
            self._cpu_static_info = self._hardware_cache.get_or_collect_hardware_info(
                self._collect_cpu_hardware_info
            )
            logger.debug("CPU static info loaded and cached in memory")

    def get_cpu_info(self) -> CPUInfo:
        """Get comprehensive CPU information and usage stats"""
        # Load static info into memory
        self._load_static_cpu_info()

        # Collect dynamic info
        usage_per_core = psutil.cpu_percent(interval=None, percpu=True)
        total_usage = psutil.cpu_percent(interval=None)

        with Path.open(Path("/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq")) as f:
            current_speed_ghz = int(f.read().strip()) / 1_000_000  # kHz to GHz

        processes = len(psutil.pids())

        with Path.open(Path("/proc/loadavg")) as f:
            parts = f.read().split()
            threads = int(parts[3].split("/")[1])

        file_descriptors = psutil.Process().num_fds() if hasattr(psutil.Process(), "num_fds") else 0
        uptime = time.time() - psutil.boot_time()

        return CPUInfo(
            name=self._cpu_static_info["name"],
            physical_cores=self._cpu_static_info["physical_cores"],
            logical_cores=self._cpu_static_info["logical_cores"],
            usage_per_core=usage_per_core,
            total_usage=total_usage,
            current_speed_ghz=current_speed_ghz,
            max_speed_ghz=self._cpu_static_info["max_speed_ghz"],
            min_speed_ghz=self._cpu_static_info["min_speed_ghz"],
            processes=processes,
            threads=threads,
            file_descriptors=file_descriptors,
            uptime=uptime,
        )
