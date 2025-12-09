"""Disk tab view for System Monitor"""

from ContaraNAS.core.ui import (
    Progress,
    Stack,
    Stat,
    Tab,
    Text,
)

from .helpers import format_bytes


def build_disk_tab(disk: dict, index: int) -> Tab:
    """Build a single disk tab content"""
    mountpoint = disk.get("mountpoint", f"Disk {index}")
    device = disk.get("device", "")
    fs_type = disk.get("fs_type", "")

    # Use device name for tab label, falling back to mountpoint
    tab_label = device.split("/")[-1] if device else mountpoint
    tab_id = f"disk_{index}"

    total = disk.get("total", 0)
    used = disk.get("used", 0)
    free = disk.get("free", 0)
    usage = disk.get("usage_percent", 0)

    # Color based on usage
    color = "success"
    if usage > 90:
        color = "error"
    elif usage > 75:
        color = "warning"

    children = [
        # Disk info header
        Text(content=mountpoint, variant="body"),
        Text(content=f"{device} ({fs_type})" if fs_type else device, variant="muted"),
        # Usage progress bar
        Progress(value=usage, max=100, size="lg", color=color),
        # Stats
        Stack(
            direction="horizontal",
            gap="6",
            children=[
                Stat(label="Total", value=format_bytes(total)),
                Stat(label="Used", value=format_bytes(used)),
                Stat(label="Free", value=format_bytes(free)),
            ],
        ),
    ]

    # I/O stats if available
    read_speed = disk.get("read_speed", 0)
    write_speed = disk.get("write_speed", 0)
    if read_speed or write_speed:
        children.append(
            Stack(
                direction="horizontal",
                gap="6",
                children=[
                    Stat(label="Read", value=f"{format_bytes(read_speed)}/s"),
                    Stat(label="Write", value=f"{format_bytes(write_speed)}/s"),
                ],
            )
        )

    return Tab(id=tab_id, label=tab_label, icon="HardDrive", children=children)
