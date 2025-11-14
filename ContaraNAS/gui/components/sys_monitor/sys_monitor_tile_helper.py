from nicegui import ui
import plotly.graph_objects as go


def create_plotly_graph(
    history: list[float],
    color: str,
    height: int = 80,
    max_range: int = 100
) -> go.Figure:
    """Create a Plotly graph with consistent styling"""
    # Convert hex color to rgba for fill
    rgb = tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    fillcolor = f'rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, 0.3)'

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        y=history,
        mode='lines',
        fill='tozeroy',
        line={'color': color, 'width': 1},
        fillcolor=fillcolor,
        hovertemplate='%{y:.1f}%<extra></extra>',
        name=''  # Empty name to remove legend
    ))

    fig.update_layout(
        height=height,
        margin={'l': 0, 'r': 0, 't': 0, 'b': 0},
        xaxis={
            'showgrid': False,
            'showticklabels': False,
            'zeroline': False,
            'visible': False
        },
        yaxis={
            'showgrid': False,
            'showticklabels': False,
            'zeroline': False,
            'range': [0, max_range],
            'visible': False
        },
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        hovermode='closest',
        modebar={'remove': ['zoom', 'pan', 'select', 'lasso', 'zoomIn', 'zoomOut', 'autoScale', 'resetScale']}
    )

    return fig


def render_cpu_header(cpu_usage: float) -> None:
    """Render CPU section header with usage percentage"""
    with ui.row().classes("w-full items-center justify-between mb-2"):
        ui.label("CPU").classes("text-xs font-semibold text-black")
        ui.label(f"{cpu_usage:.0f}%").classes("text-xs font-bold min-w-fit text-blue-500")


def render_cpu_details(physical_cores: int, logical_cores: int, speed_ghz: float) -> None:
    """Render CPU details line"""
    ui.label(f"{physical_cores}C/{logical_cores}T @ {speed_ghz:.2f}GHz").classes(
        "text-xs text-gray-500 mt-1"
    )


def render_per_core_graphs(cpu, cpu_core_history: dict, max_history_points: int) -> dict:
    """Render individual graphs for each CPU core"""
    num_cores = len(cpu.usage_per_core)
    cols = min(4, num_cores)  # Max 4 columns

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
                    color='#1976d2',
                    height=50,
                    max_range=100
                )

                # Use config parameter directly instead of props
                ui.plotly(fig).classes("w-full")

    return cpu_core_history


def render_general_cpu_graph(cpu_usage: float, cpu_general_history: list, max_history_points: int) -> list:
    """Render single general CPU usage graph"""
    # Track general CPU history
    cpu_general_history.append(cpu_usage)
    if len(cpu_general_history) > max_history_points:
        cpu_general_history.pop(0)

    fig = create_plotly_graph(
        history=cpu_general_history,
        color='#1976d2',
        height=100,
        max_range=100
    )

    # Use config parameter directly instead of props
    ui.plotly(fig).classes("w-full")

    return cpu_general_history


def render_memory_section(memory, mem_history: list, max_history_points: int) -> list:
    """Render memory information with Task Manager style graph"""
    with ui.column().classes("w-full mb-3"):
        # Header with usage percentage
        with ui.row().classes("w-full items-center justify-between"):
            ui.label("Memory").classes("text-xs font-semibold text-black")
            ui.label(f"{memory.usage:.0f}%").classes("text-xs font-bold min-w-fit text-green-600")

        # Update history
        mem_history.append(memory.usage)
        if len(mem_history) > max_history_points:
            mem_history.pop(0)

        fig = create_plotly_graph(
            history=mem_history,
            color='#388e3c',
            height=80,
            max_range=100
        )

        # Use config parameter directly instead of props
        ui.plotly(fig).classes("w-full")

        # Memory details
        used_gb = memory.used / (1024**3)
        total_gb = memory.total / (1024**3)
        ui.label(f"{used_gb:.1f}GB / {total_gb:.1f}GB").classes(
            "text-xs text-gray-500"
        )

    return mem_history


def render_disk_summary(disks: list) -> None:
    """Render disk summary with progress bars"""
    with ui.column().classes("w-full"):
        ui.label("Disks").classes("text-xs font-semibold text-black mb-1")

        # Show only the first 3 disks in the tile
        for disk in disks[:3]:
            with ui.row().classes("w-full items-center gap-2 mb-1"):
                # Mount point label
                ui.label(disk.mountpoint).classes("text-xs w-20 truncate text-black")

                # Disk usage bar
                with ui.column().classes("flex-1"):
                    ui.linear_progress(disk.usage_percent / 100, show_value=False).props("color=orange size=8px")

                # Usage percentage
                ui.label(f"{disk.usage_percent:.0f}%").classes("text-xs font-mono w-10 text-right text-black")

        # Show count if more disks exist
        if len(disks) > 3:
            ui.label(f"+ {len(disks) - 3} more disk(s)").classes(
                "text-xs text-gray-500 mt-1"
            )
