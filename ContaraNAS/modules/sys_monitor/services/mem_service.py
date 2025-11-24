import platform
import re
import subprocess
from typing import Any

import psutil

from ContaraNAS.modules.sys_monitor.dtos import MemoryInfo, RAMInfo

from .hardware_cache_service import HardwareCacheService


class MemService:
    """Service to monitor Memory information and usage"""

    def __init__(self, os_name: str | None = None):
        self._os_name: str = os_name or platform.system()
        self._hardware_cache = HardwareCacheService()
        self.ram_sticks: list[RAMInfo] = []

    def _get_dmidecode_output(self) -> str:
        """Run dmidecode command to get RAM information (requires sudo)"""
        if self._os_name != "Linux":
            raise NotImplementedError("DMIDECODE is only supported on Linux systems.")
        return subprocess.check_output(["pkexec", "dmidecode", "--type", "17"], text=True)

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
        ram_sticks = self._parse_dmidecode(dmidecode_out)
        ram_sticks_data = [ram.__dict__ for ram in ram_sticks]
        return {"ram_sticks": ram_sticks_data}

    def _load_ram_sticks_from_cache(self) -> list[RAMInfo]:
        """Load RAM sticks from cache"""
        hardware_info = self._hardware_cache.get_or_collect_hardware_info(
            self._collect_ram_hardware_info
        )

        ram_sticks_data = hardware_info.get("ram_sticks", [])
        return [RAMInfo(**ram_data) for ram_data in ram_sticks_data]

    def get_memory_info(self) -> MemoryInfo:
        """Get comprehensive Memory information and usage stats"""
        virtual_mem = psutil.virtual_memory()
        swap_mem = psutil.swap_memory()

        # Load RAM sticks from cache if not already loaded
        if not self.ram_sticks:
            self.ram_sticks = self._load_ram_sticks_from_cache()

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
