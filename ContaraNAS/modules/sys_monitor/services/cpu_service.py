from pathlib import Path
import platform
import time

import psutil

from ContaraNAS.modules.sys_monitor.dtos import CPUInfo


class CPUService:
    """Service to monitor CPU information and usage"""

    def __init__(self, os_name: str | None = None):
        self._os_name: str = os_name or platform.system()

    def _get_cpu_name(self) -> str:
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

    def get_cpu_info(self) -> CPUInfo:
        name = self._get_cpu_name()

        physical_cores = psutil.cpu_count(logical=False) or 0
        logical_cores = psutil.cpu_count(logical=True) or 0
        usage_per_core = psutil.cpu_percent(interval=None, percpu=True)

        total_usage = psutil.cpu_percent(interval=None)

        current_speed_mhz = psutil.cpu_freq()

        processes = len(psutil.pids())
        threads = sum(p.num_threads() for p in psutil.process_iter())
        file_descriptors = psutil.Process().num_fds() if hasattr(psutil.Process(), "num_fds") else 0

        uptime = time.time() - psutil.boot_time()

        return CPUInfo(
            name=name,
            physical_cores=physical_cores,
            logical_cores=logical_cores,
            usage_per_core=usage_per_core,
            total_usage=total_usage,
            current_speed_ghz=current_speed_mhz.current / 1000 if current_speed_mhz else 0,
            max_speed_ghz=current_speed_mhz.max / 1000 if current_speed_mhz else 0,
            min_speed_ghz=current_speed_mhz.min / 1000 if current_speed_mhz else 0,
            processes=processes,
            threads=threads,
            file_descriptors=file_descriptors,
            uptime=uptime,
        )
