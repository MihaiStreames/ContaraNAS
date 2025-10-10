import platform
import re
import subprocess

import psutil
from pathlib import Path

from ContaraNAS.modules.sys_monitor.dtos import MemoryInfo, RAMInfo
from ContaraNAS.core.utils import get_cache_dir, save_json


class MemService:
    """Service to monitor Memory information and usage"""

    def __init__(self, os_name=None, ram_sticks=None):
        self.os_name = os_name or platform.system()
        self.ram_sticks = ram_sticks or []

    def __get_dmidecode_output(self) -> str:
        if self.os_name != "Linux":
            raise NotImplementedError("DMIDECODE is only supported on Linux systems.")
        return subprocess.check_output(["pkexec", "dmidecode", "--type", "17"], text=True)

    @staticmethod
    def __parse_dmidecode(data: str) -> list[RAMInfo]:
        blocks = data.split("Memory Device")
        ram_info = []

        for block in blocks[1:]:

            def get_field(label: str) -> str:
                m = re.search(rf"{label}:\s*(.*)", block)
                return m.group(1).strip() if m else ""

            size_str = get_field("Size")
            if size_str == "No Module Installed" or size_str == "":
                continue

            size = (
                float(size_str.replace("GB", "").strip())
                if "GB" in size_str
                else float(size_str.replace("MB", "").strip()) / 1024 if "MB" in size_str else 0.0
            )

            speed_str = get_field("Speed")
            speed = int(speed_str.replace("MT/s", "").strip()) if "MT/s" in speed_str else 0

            ram_info.append(
                RAMInfo(
                    locator=get_field("Locator"),
                    bank_locator=get_field("Bank Locator"),
                    size=size,
                    type=get_field("Type"),
                    speed=speed,
                    manufacturer=get_field("Manufacturer"),
                    part_number=get_field("Part Number"),
                )
            )

        return ram_info

    def __get_ram_sticks(self) -> list[RAMInfo]:
        if self.os_name == "Linux":
            dmidecode_out = self.__get_dmidecode_output()
            return self.__parse_dmidecode(dmidecode_out)
        return []

    def get_memory_info(self) -> MemoryInfo:
        virtual_mem = psutil.virtual_memory()
        swap_mem = psutil.swap_memory()

        if not self.ram_sticks:
            self.ram_sticks = self.__get_ram_sticks()
            cache_dir = Path(get_cache_dir() / "ram_info_cache.json")
            save_json(cache_dir, [ram.__dict__ for ram in self.ram_sticks])

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
            ram_sticks=self.ram_sticks
        )


if __name__ == "__main__":
    mem_service = MemService()
    print(mem_service.get_memory_info())
