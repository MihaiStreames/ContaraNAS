from ContaraNAS.core.ui import (
    Grid,
    LineChart,
    Stack,
    Stat,
    StatSmall,
    Tab,
    Text,
)

from .helpers import format_bytes


def build_memory_tab(mem: dict | None, memory_history: list[float]) -> Tab:
    """Build the Memory tab content"""
    children = []

    if not mem:
        children.append(Text(content="No memory data available", variant="muted"))
        return Tab(id="memory", label="Memory", icon="MemoryStick", children=children)

    # Extract memory data
    total = mem.get("total", 0)
    used = mem.get("used", 0)
    available = mem.get("available", 0)
    cached = mem.get("cached", 0)
    shared = mem.get("shared", 0)
    buffers = mem.get("buffers", 0)
    usage = mem.get("usage", 0)
    swap_total = mem.get("swap_total", 0)
    swap_used = mem.get("swap_used", 0)
    swap_usage = mem.get("swap_usage", 0)
    ram_sticks = mem.get("ram_sticks", [])

    # Line chart showing memory usage history (taller)
    children.append(
        LineChart(
            data=memory_history if memory_history else [0],
            max=100,
            min=0,
            height=170,
            color="success",
            fill=True,
            label=f"{usage:.1f}%",
        )
    )

    # Summary text (total RAM, type, speed)
    if ram_sticks:
        first = ram_sticks[0]
        ram_type = first.get("type", "")
        ram_speed = first.get("speed", 0)
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

    # Two grids side by side
    # Grid 1: Main stats (3x3)
    # Grid 2: RAM stick details (StatSmall stack)
    grid1_children = [
        # Row 1: Usage, In Use, Available
        Stat(label="Usage", value=f"{usage:.1f}%"),
        Stat(label="In Use", value=format_bytes(used)),
        Stat(label="Available", value=format_bytes(available)),
        # Row 2: Cached, Shared, Buffers
        Stat(label="Cached", value=format_bytes(cached)),
        Stat(label="Shared", value=format_bytes(shared) if shared else "N/A"),
        Stat(label="Buffers", value=format_bytes(buffers) if buffers else "N/A"),
        # Row 3: Swap info (always present)
        Stat(label="Swap", value=f"{swap_usage:.1f}%" if swap_total else "N/A"),
        Stat(label="Swap Used", value=format_bytes(swap_used) if swap_total else "N/A"),
        Text(content=""),  # Empty cell
    ]

    # RAM stick details
    grid2_children = []
    for stick in ram_sticks:
        locator = stick.get("locator", "Unknown")
        size = stick.get("size", 0)
        ram_type = stick.get("type", "")
        speed = stick.get("speed", 0)
        value = f"{size} GB\u00a0\u00a0\u00a0{ram_type}\u00a0\u00a0\u00a0{speed} MT/s"
        grid2_children.append(StatSmall(label=locator, value=value))

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
