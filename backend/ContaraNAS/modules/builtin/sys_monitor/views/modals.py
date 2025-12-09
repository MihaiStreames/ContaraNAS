"""Modal views for the System Monitor module"""

from ContaraNAS.core.ui import (
    Button,
    Grid,
    Modal,
    Progress,
    Stack,
    Stat,
    StatCard,
    Text,
)

from .helpers import format_bytes


def build_details_modal(
    cpu: dict | None,
    mem: dict | None,
    disks: list[dict],
    open_cpu_action,
    open_memory_action,
    open_disk_action,
) -> Modal:
    """Build the main details modal"""
    stat_cards = []

    if cpu:
        stat_cards.append(
            StatCard(
                label="CPU Usage",
                value=f"{cpu.get('total_usage', 0):.1f}%",
                icon="Cpu",
                color="default",
            )
        )
        stat_cards.append(
            StatCard(
                label="Processes",
                value=str(cpu.get("processes", 0)),
                icon="Layers",
                color="default",
            )
        )

    if mem:
        usage = mem.get("usage", 0)
        color = "success" if usage < 70 else "warning" if usage < 90 else "error"
        stat_cards.append(
            StatCard(
                label="Memory Usage",
                value=f"{usage:.1f}%",
                icon="Database",
                color=color,
            )
        )

    if disks:
        primary = disks[0]
        usage = primary.get("usage_percent", 0)
        color = "success" if usage < 70 else "warning" if usage < 90 else "error"
        stat_cards.append(
            StatCard(
                label="Disk Usage",
                value=f"{usage:.1f}%",
                icon="HardDrive",
                color=color,
            )
        )

    return Modal(
        id="sys_monitor_details",
        title="System Overview",
        size="md",
        children=[
            Grid(columns=2, gap="4", children=stat_cards),
            Stack(
                direction="horizontal",
                gap="2",
                justify="center",
                children=[
                    Button(label="CPU Details", variant="secondary", on_click=open_cpu_action),
                    Button(
                        label="Memory Details", variant="secondary", on_click=open_memory_action
                    ),
                    Button(label="Disk Details", variant="secondary", on_click=open_disk_action),
                ],
            ),
        ],
    )


def build_cpu_modal(cpu: dict | None) -> Modal:
    """Build the CPU details modal"""
    if not cpu:
        return Modal(
            id="sys_monitor_cpu",
            title="CPU Details",
            size="lg",
            children=[Text(content="No CPU data available", variant="muted")],
        )

    core_stats = []
    for i, usage in enumerate(cpu.get("usage_per_core", [])):
        core_stats.append(
            Progress(
                value=usage,
                max=100,
                label=f"Core {i}",
                sublabel=f"{usage:.1f}%",
                color="default",
            )
        )

    return Modal(
        id="sys_monitor_cpu",
        title="CPU Details",
        size="lg",
        children=[
            Stack(
                direction="vertical",
                gap="4",
                children=[
                    Text(content=cpu.get("name", "Unknown CPU"), variant="body"),
                    Grid(
                        columns=3,
                        gap="4",
                        children=[
                            StatCard(
                                label="Physical Cores",
                                value=str(cpu.get("physical_cores", 0)),
                                icon="Cpu",
                            ),
                            StatCard(
                                label="Logical Cores",
                                value=str(cpu.get("logical_cores", 0)),
                                icon="Cpu",
                            ),
                            StatCard(
                                label="Total Usage",
                                value=f"{cpu.get('total_usage', 0):.1f}%",
                                icon="Activity",
                            ),
                        ],
                    ),
                    Text(content="Per-Core Usage", variant="secondary"),
                    Stack(direction="vertical", gap="2", children=core_stats),
                    Grid(
                        columns=3,
                        gap="4",
                        children=[
                            StatCard(
                                label="Current Speed",
                                value=f"{cpu.get('current_speed_ghz', 0):.2f} GHz",
                                icon="Zap",
                            ),
                            StatCard(
                                label="Processes",
                                value=str(cpu.get("processes", 0)),
                                icon="Layers",
                            ),
                            StatCard(
                                label="Threads",
                                value=str(cpu.get("threads", 0)),
                                icon="GitBranch",
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )


def build_memory_modal(mem: dict | None) -> Modal:
    """Build the memory details modal"""
    if not mem:
        return Modal(
            id="sys_monitor_memory",
            title="Memory Details",
            size="md",
            children=[Text(content="No memory data available", variant="muted")],
        )

    total = mem.get("total", 0)
    used = mem.get("used", 0)
    available = mem.get("available", 0)
    cached = mem.get("cached", 0)
    swap_total = mem.get("swap_total", 0)
    swap_used = mem.get("swap_used", 0)

    return Modal(
        id="sys_monitor_memory",
        title="Memory Details",
        size="md",
        children=[
            Stack(
                direction="vertical",
                gap="4",
                children=[
                    Progress(
                        value=mem.get("usage", 0),
                        max=100,
                        label="RAM Usage",
                        sublabel=f"{format_bytes(used)} / {format_bytes(total)}",
                        color="default",
                    ),
                    Grid(
                        columns=3,
                        gap="4",
                        children=[
                            StatCard(label="Total", value=format_bytes(total), icon="Database"),
                            StatCard(label="Used", value=format_bytes(used), icon="Database"),
                            StatCard(
                                label="Available", value=format_bytes(available), icon="Database"
                            ),
                        ],
                    ),
                    Grid(
                        columns=2,
                        gap="4",
                        children=[
                            StatCard(label="Cached", value=format_bytes(cached), icon="Archive"),
                            StatCard(
                                label="Buffers",
                                value=format_bytes(mem.get("buffers", 0)),
                                icon="Archive",
                            ),
                        ],
                    ),
                    Text(content="Swap", variant="secondary"),
                    Progress(
                        value=mem.get("swap_usage", 0),
                        max=100,
                        label="Swap Usage",
                        sublabel=f"{format_bytes(swap_used)} / {format_bytes(swap_total)}",
                        color="warning" if mem.get("swap_usage", 0) > 50 else "default",
                    ),
                ],
            ),
        ],
    )


def build_disks_modal(disks: list[dict]) -> Modal:
    """Build the disks details modal"""
    if not disks:
        return Modal(
            id="sys_monitor_disks",
            title="Disk Details",
            size="lg",
            children=[Text(content="No disk data available", variant="muted")],
        )

    disk_cards = []
    for disk in disks:
        usage = disk.get("usage_percent", 0)
        color = "success" if usage < 70 else "warning" if usage < 90 else "error"

        disk_cards.append(
            Stack(
                direction="vertical",
                gap="2",
                children=[
                    Text(content=disk.get("mountpoint", "Unknown"), variant="body"),
                    Text(
                        content=f"{disk.get('device', '')} ({disk.get('filesystem', '')})",
                        variant="muted",
                    ),
                    Progress(
                        value=usage,
                        max=100,
                        label="Usage",
                        sublabel=f"{disk.get('used_gb', 0):.1f} GB / {disk.get('total_gb', 0):.1f} GB",
                        color=color,
                    ),
                    Grid(
                        columns=2,
                        gap="2",
                        children=[
                            Stat(
                                label="Read", value=format_bytes(disk.get("read_speed", 0)) + "/s"
                            ),
                            Stat(
                                label="Write", value=format_bytes(disk.get("write_speed", 0)) + "/s"
                            ),
                        ],
                    ),
                ],
            )
        )

    return Modal(
        id="sys_monitor_disks",
        title="Disk Details",
        size="lg",
        children=[Stack(direction="vertical", gap="4", children=disk_cards)],
    )
