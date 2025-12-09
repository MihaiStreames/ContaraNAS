"""Tile view for the System Monitor module"""

from ContaraNAS.core.ui import Badge, Button, Stat, Tile

from .helpers import format_uptime


def build_tile(
    cpu: dict | None,
    mem: dict | None,
    disks: list[dict],
    last_update,
    open_details_action,
) -> Tile:
    """Build the dashboard tile UI component"""
    stats = []

    if cpu:
        stats.append(Stat(label="CPU", value=f"{cpu.get('total_usage', 0):.1f}%"))

    if mem:
        usage = mem.get("usage", 0)
        total_gb = mem.get("total", 0) / (1024**3)
        stats.append(Stat(label="Memory", value=f"{usage:.1f}% of {total_gb:.0f}GB"))

    if disks:
        primary_disk = disks[0]
        stats.append(
            Stat(
                label="Disk",
                value=f"{primary_disk.get('usage_percent', 0):.1f}%",
            )
        )

    if cpu and cpu.get("uptime"):
        stats.append(Stat(label="Uptime", value=format_uptime(cpu["uptime"])))

    return Tile(
        icon="Activity",
        title="System Monitor",
        badge=Badge(text="Live", variant="success") if last_update else None,
        stats=stats,
        actions=[
            Button(label="Details", variant="secondary", on_click=open_details_action),
        ],
    )
