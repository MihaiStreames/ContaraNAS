from nicegui import ui
import plotly.graph_objects as go
import platform

from ContaraNAS.modules.sys_monitor.constants import (
    CPU_GRAPH_HEIGHT,
    MAX_GRID_COLUMNS,
    MEMORY_GRAPH_HEIGHT,
    PER_CORE_GRAPH_HEIGHT,
)


def create_plotly_graph(
    history: list[float], color: str, height: int = 80, max_range: int = 100
) -> go.Figure:
    """Create a Plotly graph with consistent styling"""
    # Convert hex color to rgba for fill
    rgb = tuple(int(color.lstrip("#")[i : i + 2], 16) for i in (0, 2, 4))
    fillcolor = f"rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, 0.3)"

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            y=history,
            mode="lines",
            fill="tozeroy",
            line={"color": color, "width": 1},
            fillcolor=fillcolor,
            hovertemplate="%{y:.1f}%<extra></extra>",
            name="",
        )
    )

    fig.update_layout(
        height=height,
        margin={"l": 0, "r": 0, "t": 0, "b": 0},
        xaxis={"showgrid": False, "showticklabels": False, "zeroline": False, "visible": False},
        yaxis={
            "showgrid": False,
            "showticklabels": False,
            "zeroline": False,
            "range": [0, max_range],
            "visible": False,
        },
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        hovermode="closest",
        modebar={
            "remove": [
                "zoom",
                "pan",
                "select",
                "lasso",
                "zoomIn",
                "zoomOut",
                "autoScale",
                "resetScale",
            ]
        },
    )

    return fig


def render_per_core_graphs(cpu, cpu_core_history: dict, max_history_points: int) -> dict:
    """Render individual graphs for each CPU core"""
    num_cores = len(cpu.usage_per_core)
    cols = min(MAX_GRID_COLUMNS, num_cores)

    with ui.grid(columns=cols).classes("w-full gap-1"):
        for i, core_usage in enumerate(cpu.usage_per_core):
            # Track history for this core
            if i not in cpu_core_history:
                cpu_core_history[i] = []

            cpu_core_history[i].append(core_usage)
            if len(cpu_core_history[i]) > max_history_points:
                cpu_core_history[i].pop(0)

            # Create mini graph for this core
            with ui.column().classes("w-full"):
                # Core label with usage
                ui.label(f"Core {i}: {core_usage:.0f}%").classes("text-[10px] text-black")

                fig = create_plotly_graph(
                    history=cpu_core_history[i],
                    color="#1976d2",
                    height=PER_CORE_GRAPH_HEIGHT,
                    max_range=100,
                )

                # Use config parameter directly instead of props
                ui.plotly(fig).classes("w-full")

    return cpu_core_history


def render_general_cpu_graph(cpu, cpu_general_history: list, max_history_points: int) -> list:
    """Render single general CPU usage graph"""
    # Track general CPU history
    cpu_general_history.append(cpu.total_usage)
    if len(cpu_general_history) > max_history_points:
        cpu_general_history.pop(0)

    fig = create_plotly_graph(
        history=cpu_general_history, color="#1976d2", height=CPU_GRAPH_HEIGHT, max_range=100
    )

    # Use config parameter directly instead of props
    ui.plotly(fig).classes("w-full")

    return cpu_general_history


def render_cpu_tab(
    cpu,
    show_per_core: bool,
    cpu_core_history: dict,
    cpu_general_history: list,
    max_history_points: int,
    toggle_view_callback,
) -> tuple[dict, list]:
    """Render CPU tab content with graphs and information"""
    # Add context menu for switching views
    with ui.context_menu():
        ui.menu_item(
            "Switch to General View" if show_per_core else "Switch to Per-Core View",
            on_click=toggle_view_callback,
        )

    # CPU name above graph
    ui.label(cpu.name).classes("text-base font-bold text-gray-700 mb-2")

    # Main graph section
    if show_per_core:
        # Per-core graphs in a grid
        cpu_core_history = render_per_core_graphs(cpu, cpu_core_history, max_history_points)
    else:
        # General CPU graph
        cpu_general_history = render_general_cpu_graph(cpu, cpu_general_history, max_history_points)

    # Main information below graph
    with ui.row().classes("w-full items-center gap-6 mb-2 mt-3"):
        # Primary metrics
        ui.label(f"Speed: {cpu.current_speed_ghz:.2f} GHz").classes(
            "text-sm font-semibold text-gray-800"
        )
        with ui.row().classes("items-center gap-1"):
            ui.label("Usage:").classes("text-sm font-semibold text-gray-800")
            ui.label(f"{cpu.total_usage:.1f}%").classes("text-sm font-semibold text-blue-600")

        # Format uptime as dd:hh:mm:ss
        days = int(cpu.uptime // 86400)
        hours = int((cpu.uptime % 86400) // 3600)
        minutes = int((cpu.uptime % 3600) // 60)
        seconds = int(cpu.uptime % 60)
        ui.label(f"Uptime: {days:02d}:{hours:02d}:{minutes:02d}:{seconds:02d}").classes(
            "text-sm font-semibold text-gray-800"
        )

    # Secondary information (regrouped in 2 columns, 3 rows)
    with ui.grid(columns=2).classes("w-full gap-x-8 gap-y-1 text-xs text-gray-600"):
        # Row 1
        ui.label(f"Cores: {cpu.physical_cores}P / {cpu.logical_cores}L")
        ui.label(f"Threads: {cpu.threads}")
        # Row 2
        ui.label(f"Max: {cpu.max_speed_ghz:.2f} GHz")
        ui.label(f"Processes: {cpu.processes}")
        # Row 3
        ui.label(f"Min: {cpu.min_speed_ghz:.2f} GHz")

        # Windows support
        system = platform.system()
        fd_label = "Handles" if system == "Windows" else "File Descriptors"
        ui.label(f"{fd_label}: {cpu.file_descriptors}")

    return cpu_core_history, cpu_general_history


def render_ram_tab(memory, mem_history: list, max_history_points: int) -> list:
    """Render RAM tab content with graph and information"""
    # Calculate values
    # total_gb = memory.total / (1024**3)
    used_gb = memory.used / (1024**3)
    free_gb = memory.free / (1024**3)
    buffers_gb = memory.buffers / (1024**3)
    cached_gb = memory.cached / (1024**3)
    shared_gb = memory.shared / (1024**3)
    swap_total_gb = memory.swap_total / (1024**3)
    swap_used_gb = memory.swap_used / (1024**3)

    # Main graph section
    mem_history.append(memory.usage)
    if len(mem_history) > max_history_points:
        mem_history.pop(0)

    fig = create_plotly_graph(
        history=mem_history, color="#388e3c", height=MEMORY_GRAPH_HEIGHT, max_range=100
    )
    ui.plotly(fig).classes("w-full")

    # Main information below graph
    with ui.row().classes("w-full items-center gap-6 mb-2 mt-3"):
        # Primary metrics
        with ui.row().classes("items-center gap-1"):
            ui.label("Usage:").classes("text-base font-bold text-gray-800")
            ui.label(f"{memory.usage:.1f}%").classes("text-base font-bold text-green-600")
        ui.label(f"Used: {used_gb:.1f} GB").classes("text-base font-bold text-gray-800")
        ui.label(f"Free: {free_gb:.1f} GB").classes("text-base font-bold text-gray-800")

    # Secondary information
    with ui.row().classes("w-full items-center gap-4 text-xs text-gray-600"):
        ui.label(f"Buffers: {buffers_gb:.1f} GB")
        ui.label(f"Cached: {cached_gb:.1f} GB")
        ui.label(f"Shared: {shared_gb:.1f} GB")
        ui.label(f"Swap: {swap_used_gb:.1f} / {swap_total_gb:.1f} GB ({memory.swap_usage:.1f}%)")

    # Physical RAM Sticks (if available)
    if memory.ram_sticks and len(memory.ram_sticks) > 0:
        ui.separator().classes("my-3")
        ui.label("Physical RAM Modules").classes("text-sm font-semibold mb-2")

        for i, ram in enumerate(memory.ram_sticks):
            with ui.row().classes(
                "w-full items-center gap-2 mb-1 text-xs border border-black rounded p-2"
            ):
                ui.label(f"{i + 1}.").classes("w-4 text-gray-500")
                ui.label(f"{ram.size:.0f}GB").classes("font-semibold w-12")
                ui.label(ram.type).classes("w-16")
                ui.label(f"{ram.speed} MT/s").classes("w-20")
                ui.label(ram.locator).classes("w-28 text-gray-600")
                ui.label(ram.manufacturer).classes("flex-1 text-gray-600 truncate")

    return mem_history


def render_disks_tab(disks: list) -> None:
    """Render disks tab content with detailed disk information"""
    for disk in disks:
        # Calculate speeds
        read_speed_mb = disk.read_speed / (1024**2)
        write_speed_mb = disk.write_speed / (1024**2)
        read_gb = disk.read_bytes / (1024**3)
        write_gb = disk.write_bytes / (1024**3)

        # Wrap each disk in a bordered container
        with ui.column().classes("w-full border border-black rounded p-3 mb-3"):
            # Disk header
            with ui.row().classes("w-full items-center gap-2 mb-2"):
                ui.label(disk.mountpoint or disk.device).classes("text-base font-bold")
                ui.label(f"{disk.type}").classes(
                    "text-xs text-white bg-blue-500 px-1 py-0.5 rounded"
                )
                ui.label(disk.model).classes("flex-1 text-xs text-gray-600 truncate text-right")

            # Large usage bar
            with ui.row().classes("w-full items-center gap-2 mb-2"):
                with ui.column().classes("flex-1"):
                    ui.linear_progress(disk.usage_percent / 100, show_value=False).props(
                        "color=orange size=20px"
                    )
                ui.label(f"{disk.usage_percent:.1f}%").classes(
                    "text-base font-bold w-16 text-right"
                )

            # Capacity info
            ui.label(
                f"{disk.used_gb:.1f} / {disk.total_gb:.1f} GB (Free: {disk.free_gb:.1f} GB)"
            ).classes("text-xs text-gray-600 mb-2")

            # Main information
            with ui.row().classes("w-full items-center gap-6 mb-1"):
                # Primary metrics
                ui.label(f"Read: {read_speed_mb:.1f} MB/s").classes(
                    "text-sm font-semibold text-gray-800"
                )
                ui.label(f"Write: {write_speed_mb:.1f} MB/s").classes(
                    "text-sm font-semibold text-gray-800"
                )
                ui.label(f"Busy: {disk.busy_time:.1f}%").classes(
                    "text-sm font-semibold text-orange-600"
                )

            # Secondary information
            with ui.grid(columns=3).classes("w-full gap-x-4 gap-y-1 text-xs text-gray-600"):
                # Column 1
                ui.label(f"Device: {disk.device}").classes("font-mono")
                ui.label(f"Total Write: {write_gb:.1f} GB")
                # Column 2
                ui.label(f"I/O Time: {disk.io_time} ms")
                ui.label(f"FS: {disk.filesystem}").classes("font-mono")
                # Column 3
                ui.label(f"Total Read: {read_gb:.1f} GB")
