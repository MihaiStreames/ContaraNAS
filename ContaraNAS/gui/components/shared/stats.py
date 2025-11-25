from collections.abc import Callable
from dataclasses import dataclass

from nicegui import ui


# TODO: Colors shared in a common theme file
STAT_COLORS = {
    "default": "text-gray-800",
    "muted": "text-gray-600",
    "primary": "text-blue-600",
    "success": "text-green-600",
    "warning": "text-orange-600",
    "danger": "text-red-600",
}


@dataclass
class StatItem:
    """Configuration for a single stat display"""

    label: str
    value: str
    color: str = "text-gray-800"
    unit: str = ""


def stat_label(
    label: str,
    value: str,
    color: str = "text-gray-800",
    *,
    unit: str = "",
    size: str = "text-sm",
) -> ui.row:
    """Single stat display with label and value

    Usage::

        stat_label("CPU Usage", "75.5", color="text-blue-600", unit="%")
        # Renders: "CPU Usage: 75.5%"
    """
    display_value = f"{value}{unit}" if unit else value

    with ui.row().classes("items-center gap-1") as row:
        ui.label(f"{label}:").classes(f"{size} font-semibold text-gray-800")
        ui.label(display_value).classes(f"{size} font-semibold {color}")

    return row


def stat_row(
    stats: list[StatItem | tuple[str, str] | tuple[str, str, str]],
    gap: str = "gap-6",
    size: str = "text-sm",
) -> ui.row:
    """Row of stats displayed horizontally

    Usage::

        stat_row(
            [
                StatItem("Speed", "3.50", unit=" GHz"),
                StatItem("Usage", "75%", color="text-blue-600"),
                ("Simple", "value"),  # Uses default color
                ("Colored", "value", "text-green-600"),  # With color
            ]
        )
    """
    with ui.row().classes(f"w-full items-center {gap}") as row:
        for stat in stats:
            if isinstance(stat, StatItem):
                stat_label(stat.label, stat.value, stat.color, unit=stat.unit, size=size)
            elif len(stat) == 3:
                stat_label(stat[0], stat[1], stat[2], size=size)
            else:
                stat_label(stat[0], stat[1], size=size)

    return row


def stat_grid(
    stats: list[tuple[str, str]],
    columns: int = 2,
    gap_x: str = "gap-x-8",
    gap_y: str = "gap-y-1",
    size: str = "text-xs",
    color: str = "text-gray-600",
) -> ui.grid:
    """Grid of stats for secondary/detailed information

    Usage::

        stat_grid(
            [
                ("Cores", "8P / 16L"),
                ("Threads", "256"),
                ("Max Speed", "4.50 GHz"),
                ("Processes", "342"),
            ],
            columns=2,
        )
    """
    with ui.grid(columns=columns).classes(f"w-full {gap_x} {gap_y} {size} {color}") as grid:
        for label, value in stats:
            ui.label(f"{label}: {value}")

    return grid


def stat_with_icon(
    icon: str,
    label: str,
    value: str,
    *,
    icon_color: str = "text-gray-500",
    value_color: str = "text-gray-800",
) -> ui.row:
    """Stat display with leading icon

    Usage::

        stat_with_icon("memory", "RAM", "16 GB", value_color="text-blue-600")
    """
    with ui.row().classes("items-center gap-2") as row:
        ui.icon(icon).classes(icon_color)
        ui.label(f"{label}:").classes("text-sm text-gray-600")
        ui.label(value).classes(f"text-sm font-semibold {value_color}")

    return row


@ui.refreshable
def refreshable_stat(
    label: str,
    get_value: Callable[[], str],
    color: str = "text-gray-800",
    *,
    unit: str = "",
) -> ui.row:
    """A stat that can be refreshed independently

    Usage::

        cpu_stat = refreshable_stat(
            "CPU", lambda: f"{cpu.usage:.1f}", "text-blue-600", unit="%"
        )
        # Later:
        cpu_stat.refresh()
    """
    return stat_label(label, get_value(), color, unit=unit)


def primary_stats_row(
    stats: list[StatItem | tuple[str, str] | tuple[str, str, str]],
    margin: str = "mb-2 mt-3",
) -> ui.row:
    """Primary stats row with larger text for main metrics

    Usage::

        primary_stats_row(
            [
                ("Speed", "3.50 GHz"),
                ("Usage", "75.5%", "text-blue-600"),
                ("Uptime", "02:15:30:45"),
            ]
        )
    """
    with ui.row().classes(f"w-full items-center gap-6 {margin}") as row:
        for stat in stats:
            if isinstance(stat, StatItem):
                stat_label(stat.label, f"{stat.value}{stat.unit}", stat.color, size="text-base")
            elif len(stat) == 3:
                stat_label(stat[0], stat[1], stat[2], size="text-base")
            else:
                stat_label(stat[0], stat[1], size="text-base")

    return row


def secondary_stats_grid(
    stats: list[tuple[str, str]],
    columns: int = 2,
) -> ui.grid:
    """Secondary stats grid with smaller text for detailed info"""
    return stat_grid(stats, columns=columns)
