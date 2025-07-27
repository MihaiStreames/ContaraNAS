import glob
import os
from typing import Any, Dict

from ..models.memory_info import MemoryInfo
from ..utils.sys_parsers import parse_meminfo
from .linux_monitor import LinuxMonitor


class MemoryMonitorService(LinuxMonitor):
    """Service for monitoring memory metrics"""

    def get_info(self) -> MemoryInfo:
        """Get comprehensive RAM information"""
        # Parse /proc/meminfo for detailed memory info
        meminfo = parse_meminfo()

        # Convert kB to GB and calculate usage
        total_gb = meminfo["MemTotal"]
        available_gb = meminfo["MemAvailable"]
        free_gb = meminfo["MemFree"]
        used_gb = total_gb - available_gb
        usage_percent = round((used_gb / total_gb) * 100, 2)

        # Buffer and cache info
        buffers_gb = meminfo.get("Buffers", 0)
        cached_gb = meminfo.get("Cached", 0)
        shared_gb = meminfo.get("Shmem", 0)

        # Swap information
        swap_total_gb = meminfo.get("SwapTotal", 0)
        swap_free_gb = meminfo.get("SwapFree", 0)
        swap_used_gb = swap_total_gb - swap_free_gb

        swap_usage_percent = 0.0
        if swap_total_gb > 0:
            swap_usage_percent = round((swap_used_gb / swap_total_gb) * 100, 2)

        # Additional memory metrics
        dirty_gb = meminfo.get("Dirty", 0)
        writeback_gb = meminfo.get("Writeback", 0)

        # Hardware info
        hw_info = self._get_ram_hardware_info()

        return MemoryInfo(
            total_gb=total_gb,
            available_gb=available_gb,
            free_gb=free_gb,
            used_gb=used_gb,
            usage_percent=usage_percent,
            buffers_gb=buffers_gb,
            cached_gb=cached_gb,
            shared_gb=shared_gb,
            swap_total_gb=swap_total_gb,
            swap_used_gb=swap_used_gb,
            swap_free_gb=swap_free_gb,
            swap_usage_percent=swap_usage_percent,
            dirty_gb=dirty_gb,
            writeback_gb=writeback_gb,
            **hw_info,
        )

    @staticmethod
    def _get_ram_hardware_info() -> Dict[str, Any]:
        """Get RAM hardware info (works in user mode for most info)"""
        ram_hw = {}

        try:
            # Get memory controller info
            mem_controllers = glob.glob("/sys/devices/system/memory/memory*")
            if mem_controllers:
                ram_hw["memory_blocks"] = len(mem_controllers)

            # Get page size
            ram_hw["page_size_kb"] = (
                os.sysconf(os.sysconf_names["SC_PAGE_SIZE"]) // 1024
            )

        except (OSError, KeyError):
            pass

        # Fallback values
        if "speed_mhz" not in ram_hw:
            ram_hw["speed_mhz"] = "N/A (need root for dmidecode)"
        if "slots_used" not in ram_hw:
            ram_hw["slots_used"] = "N/A (need root for dmidecode)"

        return ram_hw
