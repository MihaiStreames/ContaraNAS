"""Memory tab view for System Monitor"""

from ContaraNAS.core.ui import (
    LineChart,
    Progress,
    Stack,
    Stat,
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

    # Line chart showing memory usage history
    children.append(
        LineChart(
            data=memory_history if memory_history else [0],
            max=100,
            min=0,
            height=80,
            color="success",
            fill=True,
            label=f"{mem.get('usage', 0):.1f}%",
        )
    )

    # Memory stats
    total = mem.get("total", 0)
    used = mem.get("used", 0)
    available = mem.get("available", 0)
    cached = mem.get("cached", 0)
    usage = mem.get("usage", 0)

    children.append(
        Text(
            content=f"{format_bytes(used)} / {format_bytes(total)} ({usage:.1f}%)",
            variant="body",
        )
    )

    # Main RAM progress
    children.append(Progress(value=usage, max=100, size="lg", label="RAM"))

    # Swap if present
    swap_total = mem.get("swap_total", 0)
    if swap_total > 0:
        swap_used = mem.get("swap_used", 0)
        swap_usage = (swap_used / swap_total * 100) if swap_total else 0
        children.append(
            Stack(
                direction="vertical",
                gap="xs",
                children=[
                    Text(
                        content=f"Swap: {format_bytes(swap_used)} / {format_bytes(swap_total)}",
                        variant="muted",
                    ),
                    Progress(value=swap_usage, max=100, size="sm"),
                ],
            )
        )

    # Additional stats
    stats_children = [Stat(label="Available", value=format_bytes(available))]
    if cached:
        stats_children.append(Stat(label="Cached", value=format_bytes(cached)))

    children.append(
        Stack(
            direction="horizontal",
            gap="6",
            children=stats_children,
        )
    )

    return Tab(id="memory", label="Memory", icon="MemoryStick", children=children)
