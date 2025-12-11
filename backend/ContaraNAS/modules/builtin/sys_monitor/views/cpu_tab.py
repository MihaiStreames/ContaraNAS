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

from ..dtos import CPUInfo
from .helpers import format_uptime


def build_cpu_tab(cpu: CPUInfo | None, cpu_history: Sequence[float]) -> Tab:
    """Build the CPU tab content"""
    children = []

    if not cpu:
        children.append(Text(content="No CPU data available", variant="muted"))
        return Tab(id="cpu", label="CPU", icon="Cpu", children=children)

    # Extract CPU data
    usage = cpu.total_usage
    current_speed = cpu.current_speed_ghz
    min_speed = cpu.min_speed_ghz  # Base speed
    max_speed = cpu.max_speed_ghz  # Max turbo speed
    cpu_name = cpu.name
    processes = cpu.processes
    threads = cpu.threads
    file_descriptors = cpu.file_descriptors
    uptime = cpu.uptime
    physical_cores = cpu.physical_cores
    logical_cores = cpu.logical_cores

    # Line chart for CPU usage history
    children.append(
        LineChart(
            data=list(cpu_history) if cpu_history else [0],
            max=100,
            min=0,
            height=170,
            color="primary",
            fill=True,
            label=f"{usage:.1f}%",
        )
    )

    # CPU Name
    children.append(
        Text(
            content=cpu_name,
            variant="body",
            size="xl",
        )
    )

    # Grid 1: Main stats
    # Grid 2: Hardware specs
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
