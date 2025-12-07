import re
import shutil
import subprocess
from typing import Any

from ContaraNAS.core.utils import get_logger
from ContaraNAS.modules.builtin.sys_monitor.dtos import MemoryInfo, RAMInfo
from ContaraNAS.modules.builtin.sys_monitor.services import HardwareCacheService, MemService
import psutil


logger = get_logger(__name__)


class MemServiceLinux(MemService):
    """Linux-specific Memory monitoring implementation"""

    def __init__(self):
        self._hardware_cache = HardwareCacheService(cache_name="memory")
        self._dmidecode_flag: bool | None = None
        self.ram_sticks: list[RAMInfo] | None = None

    def _check_dmidecode_available(self) -> bool:
        """Check if dmidecode is available on the system"""
        if self._dmidecode_flag is None:
            self._dmidecode_flag = shutil.which("dmidecode") is not None
            if not self._dmidecode_flag:
                logger.warning("dmidecode not found - RAM stick details will be unavailable")
        return self._dmidecode_flag

    def _get_dmidecode_output(self) -> str | None:
        """Run dmidecode command to get RAM information (requires sudo)"""
        if not self._check_dmidecode_available():
            return None

        try:
            return subprocess.check_output(
                ["pkexec", "dmidecode", "--type", "17"],
                text=True,
                timeout=30,
            )
        except subprocess.TimeoutExpired:
            logger.error("dmidecode timed out")
            return None
        except subprocess.CalledProcessError as e:
            logger.error(f"dmidecode failed: {e}")
            return None
        except FileNotFoundError:
            logger.error("pkexec not found")
            return None

    @staticmethod
    def _parse_dmidecode(data: str) -> list[RAMInfo]:
        """Parse dmidecode output to extract RAM information"""
        blocks = data.split("Memory Device")
        ram_info = []

        def get_field(block_data: str, label: str) -> str:
            """Extract a field value from a dmidecode block"""
            m = re.search(rf"{label}:\s*(.*)", block_data)
            return m.group(1).strip() if m else ""

        for block in blocks[1:]:
            size_str = get_field(block, "Size")
            if size_str in {"No Module Installed", ""}:
                continue

            size = (
                float(size_str.replace("GB", "").strip())
                if "GB" in size_str
                else float(size_str.replace("MB", "").strip()) / 1024
                if "MB" in size_str
                else 0.0
            )

            speed_str = get_field(block, "Speed")
            speed = int(speed_str.replace("MT/s", "").strip()) if "MT/s" in speed_str else 0

            ram_info.append(
                RAMInfo(
                    locator=get_field(block, "Locator"),
                    bank_locator=get_field(block, "Bank Locator"),
                    size=size,
                    type=get_field(block, "Type"),
                    speed=speed,
                    manufacturer=get_field(block, "Manufacturer"),
                    part_number=get_field(block, "Part Number"),
                )
            )

        return ram_info

    def _collect_ram_hardware_info(self) -> dict[str, Any]:
        """Collect RAM hardware info (requires sudo)"""
        dmidecode_out = self._get_dmidecode_output()

        if dmidecode_out is None:
            logger.info("Skipping RAM hardware info collection, dmidecode unavailable")
            return {"ram_sticks": [], "dmidecode_available": False}

        ram_sticks = self._parse_dmidecode(dmidecode_out)
        ram_sticks_data = [ram.__dict__ for ram in ram_sticks]
        return {"ram_sticks": ram_sticks_data, "dmidecode_available": True}

    def _load_ram_sticks(self) -> None:
        """Load RAM sticks from cache or collect it"""
        if self.ram_sticks is None:
            hardware_info = self._hardware_cache.get_or_collect_hardware_info(
                self._collect_ram_hardware_info
            )
            ram_sticks_data = hardware_info.get("ram_sticks", [])
            self.ram_sticks = [RAMInfo(**ram_data) for ram_data in ram_sticks_data]
            logger.debug(f"RAM sticks info loaded: {len(self.ram_sticks)} sticks")

    def get_memory_info(self) -> MemoryInfo:
        """Get comprehensive Memory information and usage stats"""
        virtual_mem = psutil.virtual_memory()
        swap_mem = psutil.swap_memory()

        # Load RAM sticks from cache into memory
        self._load_ram_sticks()

        return MemoryInfo(
            total=virtual_mem.total,
            available=virtual_mem.available,
            free=virtual_mem.free,
            used=virtual_mem.used,
            usage=virtual_mem.percent,
            buffers=virtual_mem.buffers,
            cached=virtual_mem.cached,
            shared=virtual_mem.shared,
            swap_total=swap_mem.total,
            swap_used=swap_mem.used,
            swap_free=swap_mem.free,
            swap_usage=swap_mem.percent,
            ram_sticks=self.ram_sticks,
        )
