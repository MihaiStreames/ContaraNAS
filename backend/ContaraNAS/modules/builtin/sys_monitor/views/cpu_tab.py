from ContaraNAS.core.ui import (
    Grid,
    LineChart,
    Stack,
    Stat,
    StatSmall,
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

    # Extract CPU data
    usage = cpu.get("total_usage", 0)
    current_speed = cpu.get("current_speed_ghz", 0)
    min_speed = cpu.get("min_speed_ghz", 0)  # Base speed
    max_speed = cpu.get("max_speed_ghz", 0)  # Max turbo speed
    cpu_name = cpu.get("name", "Unknown CPU")
    processes = cpu.get("processes", 0)
    threads = cpu.get("threads", 0)
    file_descriptors = cpu.get("file_descriptors", 0)
    uptime = cpu.get("uptime", 0)
    physical_cores = cpu.get("physical_cores", 0)
    logical_cores = cpu.get("logical_cores", 0)

    # Line chart showing CPU usage history (taller)
    children.append(
        LineChart(
            data=cpu_history if cpu_history else [0],
            max=100,
            min=0,
            height=170,
            color="primary",
            fill=True,
            label=f"{usage:.1f}%",
        )
    )

    # CPU name (large text)
    children.append(
        Text(
            content=cpu_name,
            variant="body",
            size="xl",
        )
    )

    # Two grids side by side
    # Grid 1: Main stats (3x3, not all filled)
    # Grid 2: Hardware specs (4 rows, shown as vertical list)
    grid1_children = [
        # Row 1
        Stat(label="Usage", value=f"{usage:.1f}%"),
        Stat(label="Speed", value=f"{current_speed:.2f} GHz" if current_speed else "N/A"),
        Text(content=""),  # Empty cell
        # Row 2
        Stat(label="Processes", value=str(processes)),
        Stat(label="Threads", value=str(threads)),
        Stat(label="File Desc.", value=str(file_descriptors)),
        # Row 3
        Stat(label="Uptime", value=format_uptime(uptime) if uptime else "N/A"),
        Text(content=""),  # Empty cell
        Text(content=""),  # Empty cell
    ]

    grid2_children = [
        StatSmall(label="Base Speed", value=f"{min_speed:.2f} GHz" if min_speed else "N/A"),
        StatSmall(label="Max Speed", value=f"{max_speed:.2f} GHz" if max_speed else "N/A"),
        StatSmall(label="Cores", value=str(physical_cores)),
        StatSmall(label="Logical Processors", value=str(logical_cores)),
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

    return Tab(id="cpu", label="CPU", icon="Cpu", children=children)
