from ContaraNAS.core.ui import (
    Grid,
    LineChart,
    Stack,
    Stat,
    StatSmall,
    Tab,
    Text,
)

from .helpers import format_bytes, format_io_time


def build_disk_tab(disk: dict, index: int, disk_history: list[float]) -> Tab:
    """Build a single disk tab content"""
    children = []

    # Extract disk data
    device = disk.get("device", "")
    mountpoint = disk.get("mountpoint", f"Disk {index}")
    filesystem = disk.get("filesystem", "")
    disk_type = disk.get("type", "Unknown")
    model = disk.get("model", "")

    total_gb = disk.get("total_gb", 0)
    used_gb = disk.get("used_gb", 0)
    free_gb = disk.get("free_gb", 0)
    usage = disk.get("usage_percent", 0)

    read_speed = disk.get("read_speed", 0)
    write_speed = disk.get("write_speed", 0)
    busy_time = disk.get("busy_time", 0)

    read_bytes = disk.get("read_bytes", 0)
    write_bytes = disk.get("write_bytes", 0)
    io_time = disk.get("io_time", 0)

    # Tab label and ID
    tab_label = device.split("/")[-1] if device else mountpoint
    tab_id = f"disk_{index}"

    # Line chart showing busy_time % history
    children.append(
        LineChart(
            data=disk_history if disk_history else [0],
            max=100,
            min=0,
            height=170,
            color="warning",
            fill=True,
            label=f"{busy_time:.1f}%",
        )
    )

    # Model name as summary text
    summary = model if model else f"{disk_type} Disk"
    children.append(
        Text(
            content=summary,
            variant="body",
            size="xl",
        )
    )

    # Two grids side by side
    # Grid 1: Main stats (3x3)
    # Grid 2: Hardware info (StatSmall stack)
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
        StatSmall(label="Type", value=disk_type),
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
