"""CPU tab view for System Monitor"""

from ContaraNAS.core.ui import (
    Grid,
    LineChart,
    Progress,
    Stack,
    Stat,
    Tab,
    Text,
)

from .helpers import format_uptime


def build_cpu_tab(cpu: dict | None, cpu_history: list[float]) -> Tab:
    """Build the CPU tab content"""
    children = []

    if not cpu:
        children.append(Text(content="No CPU data available", variant="muted"))
        return Tab(id="cpu", label="CPU", icon="Cpu", children=children)

    # Line chart showing CPU usage history
    children.append(
        LineChart(
            data=cpu_history if cpu_history else [0],
            max=100,
            min=0,
            height=80,
            color="primary",
            fill=True,
            label=f"{cpu.get('total_usage', 0):.1f}%",
        )
    )

    # CPU info header
    cpu_name = cpu.get("model", "Unknown CPU")
    freq = cpu.get("frequency_current", 0)
    freq_str = f"{freq / 1000:.2f} GHz" if freq else ""
    usage = cpu.get("total_usage", 0)

    children.append(
        Text(
            content=cpu_name,
            variant="muted",
        )
    )

    stats_children = [Stat(label="Usage", value=f"{usage:.1f}%")]
    if freq_str:
        stats_children.append(Stat(label="Frequency", value=freq_str))
    if cpu.get("uptime"):
        stats_children.append(Stat(label="Uptime", value=format_uptime(cpu["uptime"])))

    children.append(
        Stack(
            direction="horizontal",
            gap="6",
            children=stats_children,
        )
    )

    # Per-core usage grid
    cores = cpu.get("per_core_usage", [])
    if cores:
        core_items = []
        for i, core_usage in enumerate(cores):
            core_items.append(
                Stack(
                    direction="vertical",
                    gap="xs",
                    children=[
                        Text(content=f"Core {i}", variant="muted"),
                        Progress(value=core_usage, max=100, size="sm"),
                    ],
                )
            )

        children.append(
            Grid(
                columns=4,
                gap="md",
                children=core_items,
            )
        )

    return Tab(id="cpu", label="CPU", icon="Cpu", children=children)
