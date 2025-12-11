from collections.abc import Sequence

from ContaraNAS.core.ui import (
    Grid,
    LineChart,
    Stack,
    Stat,
    StatSmall,
    Tab,
    Text,
)

from ..dtos import MemoryInfo
from .helpers import format_bytes


def build_memory_tab(mem: MemoryInfo | None, memory_history: Sequence[float]) -> Tab:
    """Build the Memory tab content"""
    children = []

    if not mem:
        children.append(Text(content="No memory data available", variant="muted"))
        return Tab(id="memory", label="Memory", icon="MemoryStick", children=children)

    # Extract memory data
    total = mem.total
    used = mem.used
    available = mem.available
    cached = mem.cached
    shared = mem.shared
    buffers = mem.buffers
    usage = mem.usage
    swap_total = mem.swap_total
    swap_used = mem.swap_used
    swap_usage = mem.swap_usage
    ram_sticks = mem.ram_sticks  # This is a list of RAMInfo dataclasses

    # Line chart for memory usage history
    children.append(
        LineChart(
            data=list(memory_history) if memory_history else [0],
            max=100,
            min=0,
            height=170,
            color="success",
            fill=True,
            label=f"{usage:.1f}%",
        )
    )

    # Summary text
    if ram_sticks:
        first = ram_sticks[0]
        ram_type = first.type if hasattr(first, "type") else ""
        ram_speed = first.speed if hasattr(first, "speed") else 0
        summary = f"{format_bytes(total)} {ram_type}"
        if ram_speed:
            summary += f" @ {ram_speed} MT/s"
    else:
        summary = format_bytes(total)

    children.append(
        Text(
            content=summary,
            variant="body",
            size="xl",
        )
    )

    # Grid 1: Main stats
    # Grid 2: RAM stick details
    grid1_children = [
        # Row 1: Usage, In Use, Available
        Stat(label="Usage", value=f"{usage:.1f}%"),
        Stat(label="In Use", value=format_bytes(used)),
        Stat(label="Available", value=format_bytes(available)),
        # Row 2: Cached, Shared, Buffers
        Stat(label="Cached", value=format_bytes(cached)),
        Stat(label="Shared", value=format_bytes(shared) if shared else "N/A"),
        Stat(label="Buffers", value=format_bytes(buffers) if buffers else "N/A"),
        # Row 3: Swap
        Stat(label="Swap", value=f"{swap_usage:.1f}%" if swap_total else "N/A"),
        Stat(label="Swap Used", value=format_bytes(swap_used) if swap_total else "N/A"),
        Stat(label="Swap Total", value=format_bytes(swap_total) if swap_total else "N/A"),
    ]

    # RAM stick details
    grid2_children = []
    for i, stick in enumerate(ram_sticks[:4]):
        locator = stick.locator if hasattr(stick, "locator") else f"Slot {i}"
        size = stick.size if hasattr(stick, "size") else 0
        stick_type = stick.type if hasattr(stick, "type") else "Unknown"
        speed = stick.speed if hasattr(stick, "speed") else 0

        label = locator
        value = f"{size:.0f} GB {stick_type}"
        if speed:
            value += f" @ {speed}"
        grid2_children.append(StatSmall(label=label, value=value))

    if not grid2_children:
        grid2_children.append(StatSmall(label="RAM", value="Info unavailable"))

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

    return Tab(id="memory", label="Memory", icon="MemoryStick", children=children)
