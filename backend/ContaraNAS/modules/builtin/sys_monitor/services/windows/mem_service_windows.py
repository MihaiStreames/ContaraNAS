import contextlib
from typing import Any

import psutil
from win32pdh import PDH_FMT_DOUBLE
from win32pdh import AddCounter
from win32pdh import CloseQuery
from win32pdh import CollectQueryData
from win32pdh import GetFormattedCounterValue
from win32pdh import OpenQuery
import wmi

from ContaraNAS.core import get_logger
from ContaraNAS.modules.builtin.sys_monitor.dtos import MemoryInfo
from ContaraNAS.modules.builtin.sys_monitor.dtos import RAMInfo
from ContaraNAS.modules.builtin.sys_monitor.services import HardwareCacheService
from ContaraNAS.modules.builtin.sys_monitor.services import MemService


logger = get_logger(__name__)

# SMBIOS Memory Type mapping
SMBIOS_MEMORY_TYPES = {
    0: "Unknown",
    1: "Other",
    2: "DRAM",
    3: "Synchronous DRAM",
    4: "Cache DRAM",
    5: "EDO",
    6: "EDRAM",
    7: "VRAM",
    8: "SRAM",
    9: "RAM",
    10: "ROM",
    11: "Flash",
    12: "EEPROM",
    13: "FEPROM",
    14: "EPROM",
    15: "CDRAM",
    16: "3DRAM",
    17: "SDRAM",
    18: "SGRAM",
    19: "RDRAM",
    20: "DDR",
    21: "DDR2",
    22: "DDR2 FB-DIMM",
    24: "DDR3",
    26: "DDR4",
    27: "LPDDR",
    28: "LPDDR2",
    29: "LPDDR3",
    30: "LPDDR4",
    31: "Logical non-volatile device",
    34: "DDR5",
    35: "LPDDR5",
}


class MemServiceWindows(MemService):
    """Windows-specific Memory monitoring implementation"""

    def __init__(self):
        self._hardware_cache = HardwareCacheService(cache_name="memory")
        self.ram_sticks: list[RAMInfo] | None = None

        # PDH performance counter handles for cached memory
        self._query_handle = None
        self._cache_counters = {}
        self._pdh_initialized = False

    @staticmethod
    def _collect_ram_hardware_info() -> dict[str, Any]:
        """Collect RAM hardware info using WMI"""
        c = wmi.WMI()
        ram_modules = c.Win32_PhysicalMemory()
        ram_sticks = []

        for ram in ram_modules:
            smbios_type = ram.SMBIOSMemoryType
            memory_type = SMBIOS_MEMORY_TYPES.get(smbios_type, f"Unknown ({smbios_type})")

            size_gb = int(ram.Capacity) / (1024**3) if ram.Capacity else 0

            ram_sticks.append(
                {
                    "locator": ram.DeviceLocator or "Unknown",
                    "bank_locator": ram.BankLabel or "Unknown",
                    "size": size_gb,
                    "type": memory_type,
                    "speed": int(ram.Speed) if ram.Speed else 0,
                    "manufacturer": (ram.Manufacturer or "Unknown").strip(),
                    "part_number": (ram.PartNumber or "Unknown").strip(),
                }
            )

        return {"ram_sticks": ram_sticks}

    def _initialize_pdh(self) -> bool:
        """Initialize PDH performance counters for cached memory"""
        if self._pdh_initialized:
            return True

        try:
            self._query_handle = OpenQuery()

            # Add counters for all cached memory components (matches Task Manager)
            cache_counter_paths = {
                "cache_bytes": r"\Memory\Cache Bytes",
                "standby_core": r"\Memory\Standby Cache Core Bytes",
                "standby_normal": r"\Memory\Standby Cache Normal Priority Bytes",
                "standby_reserve": r"\Memory\Standby Cache Reserve Bytes",
                "modified": r"\Memory\Modified Page List Bytes",
            }

            for name, path in cache_counter_paths.items():
                self._cache_counters[name] = AddCounter(self._query_handle, path)

            # Initial collection (PDH requires two samples)
            CollectQueryData(self._query_handle)

            self._pdh_initialized = True
            logger.debug("PDH memory counters initialized")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize PDH for memory: {e}")
            return False

    def _get_cached_memory(self) -> float:
        """Get total cached memory using PDH performance counters"""
        try:
            if not self._pdh_initialized and not self._initialize_pdh():
                raise RuntimeError("PDH not initialized")

            CollectQueryData(self._query_handle)

            total_cached = 0.0
            for counter_handle in self._cache_counters.values():
                _, value = GetFormattedCounterValue(counter_handle, PDH_FMT_DOUBLE)
                total_cached += value

            return total_cached

        except Exception as e:
            logger.debug(f"Error getting cached memory from PDH: {e}")
            self.cleanup()
            return 0.0

    def cleanup(self) -> None:
        """Clean up PDH resources"""
        if self._query_handle:
            with contextlib.suppress(Exception):
                CloseQuery(self._query_handle)
            self._query_handle = None
            self._cache_counters = {}
            self._pdh_initialized = False
            logger.debug("Memory PDH resources cleaned up")

    def _load_ram_sticks(self) -> None:
        """Load RAM sticks from cache or collect it"""
        if self.ram_sticks is None:
            hardware_info = self._hardware_cache.get_or_collect_hardware_info(
                self._collect_ram_hardware_info
            )
            ram_sticks_data = hardware_info.get("ram_sticks", [])
            self.ram_sticks = [RAMInfo(**ram_data) for ram_data in ram_sticks_data]
            logger.debug("RAM sticks info loaded and cached in memory")

    def get_memory_info(self) -> MemoryInfo:
        """Get comprehensive Memory information and usage stats"""
        virtual_mem = psutil.virtual_memory()
        swap_mem = psutil.swap_memory()

        # Get cached memory from performance counters (matches Task Manager)
        cached_bytes = self._get_cached_memory()

        # Load RAM sticks from cache
        self._load_ram_sticks()

        return MemoryInfo(
            total=virtual_mem.total,
            available=virtual_mem.available,
            free=virtual_mem.free,
            used=virtual_mem.used,
            usage=virtual_mem.percent,
            buffers=0,  # Not available on Windows
            cached=cached_bytes,  # Total cached memory
            shared=0,  # Not available on Windows
            swap_total=swap_mem.total,
            swap_used=swap_mem.used,
            swap_free=swap_mem.free,
            swap_usage=swap_mem.percent,
            ram_sticks=self.ram_sticks,
        )
