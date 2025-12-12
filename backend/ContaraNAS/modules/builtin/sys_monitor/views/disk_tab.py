from collections.abc import Sequence

from ContaraNAS.core.ui import Grid
from ContaraNAS.core.ui import LineChart
from ContaraNAS.core.ui import Stack
from ContaraNAS.core.ui import Stat
from ContaraNAS.core.ui import StatSmall
from ContaraNAS.core.ui import Tab
from ContaraNAS.core.ui import Text

from ..dtos import DiskInfo
from .helpers import format_bytes
from .helpers import format_io_time


def build_disk_tab(disk: DiskInfo, index: int, disk_history: Sequence[float]) -> Tab:
    """Build a single disk tab content"""
    children = []

    # Extract disk data
    device = disk.device
    mountpoint = disk.mountpoint or f"Disk {index}"
    filesystem = disk.filesystem
    disk_type = disk.type
    model = disk.model

    total_gb = disk.total_gb
    used_gb = disk.used_gb
    free_gb = disk.free_gb
    usage = disk.usage_percent

    read_speed = disk.read_speed
    write_speed = disk.write_speed
    busy_time = disk.busy_time

    read_bytes = disk.read_bytes
    write_bytes = disk.write_bytes
    io_time = disk.io_time

    tab_label = device.split("/")[-1] if device else mountpoint
    tab_id = f"disk_{index}"

    # Line chart for disk busy time history
    children.append(
        LineChart(
            data=list(disk_history) if disk_history else [0],
            max=100,
            min=0,
            height=170,
            color="warning",
            fill=True,
            label=f"{busy_time:.1f}%",
        )
    )

    # Model name
    summary = model if model else f"{disk_type} Disk"
    children.append(
        Text(
            content=summary,
            variant="body",
            size="xl",
        )
    )

    # Grid 1: Main stats
    # Grid 2: Hardware info
    grid1_children = [
        # Row 1: Usage, Used, Free
        Stat(label="Usage", value=f"{usage:.1f}%"),
        Stat(label="Used", value=f"{used_gb:.1f} GB"),
        Stat(label="Free", value=f"{free_gb:.1f} GB"),
        # Row 2: Read Speed, Write Speed, Active %
        Stat(label="Read", value=f"{format_bytes(read_speed)}/s"),
        Stat(label="Write", value=f"{format_bytes(write_speed)}/s"),
        Stat(label="Active", value=f"{busy_time:.1f}%"),
        # Row 3: Cumulative I/O stats
        Stat(label="Total Read", value=format_bytes(read_bytes)),
        Stat(label="Total Write", value=format_bytes(write_bytes)),
        Stat(label="I/O Time", value=format_io_time(io_time) if io_time else "N/A"),
    ]

    # Hardware info
    grid2_children = [
        StatSmall(label="Type", value=disk_type if disk_type else "Unknown"),
        StatSmall(label="Filesystem", value=filesystem if filesystem else "N/A"),
        StatSmall(label="Device", value=device if device else "N/A"),
        StatSmall(label="Mountpoint", value=mountpoint),
        StatSmall(label="Total", value=f"{total_gb:.1f} GB"),
    ]

    children.append(
        Stack(
            direction="horizontal",
            gap="6",
            align="start",
            grow=True,
            children=[
                Grid(columns=3, gap="4", children=grid1_children),
                Stack(direction="vertical", gap="1", children=grid2_children),
            ],
        )
    )

    return Tab(id=tab_id, label=tab_label, icon="HardDrive", children=children)
