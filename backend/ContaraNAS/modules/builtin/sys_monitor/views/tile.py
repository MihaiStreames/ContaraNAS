from collections.abc import Sequence

from ContaraNAS.core.ui import Tabs
from ContaraNAS.core.ui import Tile

from ..dtos import CPUInfo
from ..dtos import DiskInfo
from ..dtos import MemoryInfo
from .cpu_tab import build_cpu_tab
from .disk_tab import build_disk_tab
from .memory_tab import build_memory_tab


def build_tile(
    cpu: CPUInfo | None,
    mem: MemoryInfo | None,
    disks: list[DiskInfo],
    cpu_history: Sequence[float],
    memory_history: Sequence[float],
    disk_history: dict[str, Sequence[float]],
) -> Tile:
    """Build the dashboard tile UI component with tabs"""
    tabs = [
        build_cpu_tab(cpu, cpu_history),
        build_memory_tab(mem, memory_history),
    ]

    # Add a tab for each disk
    for i, disk in enumerate(disks):
        device = disk.device
        history = disk_history.get(device, [])
        tabs.append(build_disk_tab(disk, i, history))

    return Tile(
        icon="Activity",
        title="System Monitor",
        colspan=2,
        rowspan=2,
        content=[
            Tabs(
                tabs=tabs,
                default_tab="cpu",
                size="sm",
            )
        ],
    )
