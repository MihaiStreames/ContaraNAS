import contextlib
import time
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

from ...dtos import CPUInfo
from .. import CPUService
from .. import HardwareCacheService


logger = get_logger(__name__)


class CPUServiceWindows(CPUService):
    """Windows-specific CPU monitoring implementation"""

    def __init__(self):
        self._hardware_cache = HardwareCacheService(cache_name="cpu")
        self._cpu_static_info: dict | None = None

        # PDH performance counter handles
        self._query_handle = None
        self._counter_handle = None
        self._pdh_initialized = False

    @staticmethod
    def _collect_cpu_hardware_info() -> dict[str, Any]:
        """Collect static CPU hardware info using WMI"""
        c = wmi.WMI()
        cpu = c.Win32_Processor()[0]

        name = cpu.Name.strip()
        physical_cores = cpu.NumberOfCores
        logical_cores = cpu.NumberOfLogicalProcessors

        # MaxClockSpeed is the rated/base speed in MHz
        rated_speed_ghz = cpu.MaxClockSpeed / 1000 if cpu.MaxClockSpeed else 0

        # Estimate turbo max (Intel mobile CPUs typically 2x base)
        turbo_max_ghz = rated_speed_ghz * 2.0
        min_speed_ghz = 0.8  # Intel typically idles at 800 MHz

        return {
            "name": name,
            "physical_cores": physical_cores,
            "logical_cores": logical_cores,
            "max_speed_ghz": turbo_max_ghz,
            "min_speed_ghz": min_speed_ghz,
            "rated_speed_ghz": rated_speed_ghz,
        }

    def _initialize_pdh(self) -> bool:
        """Initialize PDH performance counters"""
        if self._pdh_initialized:
            return True

        try:
            self._query_handle = OpenQuery()
            counter_path = r"\Processor Information(_Total)\% Processor Performance"
            self._counter_handle = AddCounter(self._query_handle, counter_path)

            # Initial collection (PDH requires two samples)
            CollectQueryData(self._query_handle)

            self._pdh_initialized = True
            logger.debug("PDH performance counters initialized")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize PDH: {e}")
            return False

    def _get_current_cpu_frequency(self) -> float:
        """
        Get current CPU frequency using PDH performance counters.
        Returns percentage of rated speed, which can exceed 100% with turbo boost.
        """
        try:
            if not self._pdh_initialized and not self._initialize_pdh():
                raise RuntimeError("PDH not initialized")

            CollectQueryData(self._query_handle)
            _, percentage = GetFormattedCounterValue(self._counter_handle, PDH_FMT_DOUBLE)

            # Calculate actual frequency: (percentage / 100) * rated_speed
            if self._cpu_static_info:
                rated_speed_ghz = self._cpu_static_info.get("rated_speed_ghz", 2.1)
                return (percentage / 100) * rated_speed_ghz

        except Exception as e:
            logger.debug(f"Error getting CPU frequency from PDH: {e}")
            self.cleanup()

        # Fallback to psutil
        current_freq = psutil.cpu_freq()
        return current_freq.current / 1000 if current_freq else 0

    @staticmethod
    def _get_total_handles() -> int:
        """Get total system handles (Windows equivalent of file descriptors)"""
        try:
            total_handles = 0
            for proc in psutil.process_iter(["num_handles"]):
                try:
                    handles = proc.info.get("num_handles", 0)
                    if handles:
                        total_handles += handles
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            return total_handles
        except Exception as e:
            logger.debug(f"Error getting total handles: {e}")
            return 0

    def cleanup(self) -> None:
        """Clean up PDH resources"""
        if self._query_handle:
            with contextlib.suppress(Exception):
                CloseQuery(self._query_handle)

            self._query_handle = None
            self._counter_handle = None
            self._pdh_initialized = False
            logger.debug("PDH resources cleaned up")

    def _load_static_cpu_info(self) -> None:
        """Load CPU static info from cache or collect it"""
        if self._cpu_static_info is None:
            self._cpu_static_info = self._hardware_cache.get_or_collect_hardware_info(
                self._collect_cpu_hardware_info
            )
            logger.debug("CPU static info loaded and cached in memory")

    def get_cpu_info(self) -> CPUInfo:
        """Get comprehensive CPU information and usage stats"""
        self._load_static_cpu_info()

        # Collect dynamic info
        usage_per_core = psutil.cpu_percent(interval=None, percpu=True)
        total_usage = psutil.cpu_percent(interval=None)
        current_speed_ghz = self._get_current_cpu_frequency()

        processes = len(psutil.pids())
        threads = sum(p.num_threads() for p in psutil.process_iter())
        handles = self._get_total_handles()
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
            file_descriptors=handles,
            uptime=uptime,
        )
