import os
from typing import Any, Dict

import psutil

from ..models.cpu_info import CpuInfo
from ..utils.sys_parsers import get_total_fd_count, get_uptime, parse_cpuinfo
from .linux_monitor import LinuxMonitor


class CpuMonitorService(LinuxMonitor):
    """Service for monitoring CPU metrics"""

    def get_info(self) -> CpuInfo:
        """Get comprehensive CPU information"""
        # Get CPU info from /proc/cpuinfo
        cpuinfo_data = parse_cpuinfo()

        # Get basic CPU counts
        physical_cores = psutil.cpu_count(logical=False)
        logical_cores = psutil.cpu_count(logical=True)
        sockets = len(cpuinfo_data.get("physical_ids", {0}))

        # CPU usage (get once for efficiency)
        usage_per_core = psutil.cpu_percent(interval=1, percpu=True)
        total_usage = sum(usage_per_core) / len(usage_per_core)

        # CPU frequency
        current_speed, max_speed, min_speed = self._get_cpu_frequencies(cpuinfo_data)

        # Process and thread counts
        processes = len(psutil.pids())
        threads = self._count_total_threads()

        # File descriptors
        file_descriptors = get_total_fd_count()

        # System uptime
        uptime = get_uptime()

        # Load averages
        load_avg_1m, load_avg_5m, load_avg_15m = os.getloadavg()

        return CpuInfo(
            name=cpuinfo_data.get("model_name", "Unknown"),
            physical_cores=physical_cores,
            logical_cores=logical_cores,
            sockets=sockets,
            usage_per_core=usage_per_core,
            total_usage=round(total_usage, 2),
            current_speed_ghz=current_speed,
            max_speed_ghz=max_speed,
            min_speed_ghz=min_speed,
            processes=processes,
            threads=threads,
            file_descriptors=file_descriptors,
            uptime=uptime,
            load_avg_1m=load_avg_1m,
            load_avg_5m=load_avg_5m,
            load_avg_15m=load_avg_15m,
        )

    @staticmethod
    def _get_cpu_frequencies(cpuinfo_data: Dict[str, Any]) -> tuple:
        """Get CPU frequencies"""
        cpu_freq = psutil.cpu_freq()
        if cpu_freq:
            current = cpu_freq.current
            max_freq = cpu_freq.max
            min_freq = cpu_freq.min
        else:
            # Fallback to /proc/cpuinfo
            cpu_mhz = cpuinfo_data.get("cpu_mhz", 0)
            current = cpu_mhz
            max_freq = current
            min_freq = None

        return current, max_freq, min_freq

    @staticmethod
    def _count_total_threads() -> int:
        """Count total threads across all processes"""
        total_threads = 0
        for proc in psutil.process_iter(["num_threads"]):
            try:
                total_threads += proc.info["num_threads"] or 0
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return total_threads
