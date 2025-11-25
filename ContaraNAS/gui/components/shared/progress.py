from dataclasses import dataclass

from nicegui import ui


@dataclass
class ProgressSegment:
    """Configuration for a segment in a segmented progress bar"""

    value: float  # Percentage 0-100
    color: str  # CSS color
    label: str
    size: int = 0  # Optional raw size for tooltip
    tooltip: str = ""  # Override tooltip text


def usage_bar(
    percent: float,
    *,
    color: str = "orange",
    size: str = "20px",
    show_label: bool = True,
    label_width: str = "w-16",
) -> ui.row:
    """Simple usage bar with optional percentage label

    Usage::

        usage_bar(
            75.5, color="orange", size="20px", show_label=True, label_width="w-16"
        )
    """
    with ui.row().classes("w-full items-center gap-2") as row:
        with ui.column().classes("flex-1"):
            ui.linear_progress(percent / 100, show_value=False).props(f"color={color} size={size}")

        if show_label:
            ui.label(f"{percent:.1f}%").classes(f"text-base font-bold {label_width} text-right")

    return row


def segmented_progress_bar(
    segments: list[ProgressSegment],
    height: int = 20,
    background: str = "#e0e0e0",
    border_radius: int = 4,
) -> ui.html:
    """Multi-color segmented progress bar

    Usage::

        segmented_progress_bar(
            [
                ProgressSegment(30, "#1976d2", "Games", size=1024 * 1024 * 1024 * 30),
                ProgressSegment(10, "#388e3c", "Cache", size=1024 * 1024 * 1024 * 10),
                ProgressSegment(5, "#f57c00", "Other", size=1024 * 1024 * 1024 * 5),
            ],
            height=25,
            background="#f5f5f5",
            border_radius=8,
        )
    """
    segments_html = ""
    for seg in segments:
        tooltip = seg.tooltip or seg.label
        segments_html += (
            f'<div style="background-color: {seg.color}; width: {seg.value}%; height: 100%;" '
            f'title="{tooltip}"></div>'
        )

    html = f"""
    <div style="
        width: 100%;
        height: {height}px;
        background-color: {background};
        border-radius: {border_radius}px;
        overflow: hidden;
        display: flex;
        position: relative;
    ">
        {segments_html}
    </div>
    """

    return ui.html(html, sanitize=False)


def color_legend(
    items: list[tuple[str, str, str]],
    gap: str = "gap-4",
    size: str = "text-xs",
    margin: str = "mt-1",
) -> ui.row:
    """Color legend for segmented bars

    Usage::

        color_legend(
            [
                ("#1976d2", "Games", "30.5 GB"),
                ("#388e3c", "Cache", "10.2 GB"),
            ],
            gap="gap-6",
            size="text-sm",
            margin="mt-2",
        )
    """
    with ui.row().classes(f"w-full {gap} {margin} {size}") as row:
        for color, label, value in items:
            ui.html(f'<span style="color: {color};">■</span> {label}: {value}', sanitize=False)

    return row


def mini_progress(
    percent: float,
    *,
    color: str = "primary",
    height: str = "4px",
    show_tooltip: bool = True,
) -> ui.linear_progress:
    """Minimal progress indicator for compact displays

    Usage::
        mini_progress(75.5, color="primary", height="4px", show_tooltip=True)
    """
    progress = ui.linear_progress(percent / 100, show_value=False).props(
        f"color={color} size={height}"
    )

    if show_tooltip:
        progress.tooltip(f"{percent:.1f}%")

    return progress


def circular_progress(
    percent: float,
    *,
    size: str = "60px",
    color: str = "primary",
    show_value: bool = True,
    font_size: str = "12px",
) -> ui.circular_progress:
    """Circular progress indicator

    Usage::

        circular_progress(
            75.5, color="orange", size="80px", show_value=True, font_size="14px"
        )
    """
    return ui.circular_progress(
        value=percent / 100,
        show_value=show_value,
        size=size,
        color=color,
    ).props(f"font-size={font_size}")


def usage_breakdown(
    items: list[tuple[str, float, str]],
    total_label: str = "Total",
) -> ui.column:
    """Usage breakdown with individual bars for each item

    Usage::

        usage_breakdown(
            [
                ("Games", 60, "30 GB"),
                ("Cache", 20, "10 GB"),
                ("Other", 10, "5 GB"),
            ],
            total_label="Total Used",
        )
    """
    with ui.column().classes("w-full gap-2") as container:
        for label, percent, value in items:
            with ui.row().classes("w-full items-center gap-2"):
                ui.label(label).classes("w-20 text-xs text-gray-600")
                with ui.column().classes("flex-1"):
                    ui.linear_progress(percent / 100, show_value=False).props(
                        "color=primary size=8px"
                    )
                ui.label(value).classes("w-16 text-xs text-right")

    return container


def status_indicator(
    status: str,
    color_map: dict[str, str] | None = None,
) -> ui.badge:
    """Status badge with automatic color mapping

    Usage::

        status_indicator("running")  # Green badge
        status_indicator("stopped")  # Grey badge
    """
    default_colors = {
        "running": "positive",
        "enabled": "positive",
        "active": "positive",
        "online": "positive",
        "stopped": "grey",
        "disabled": "grey",
        "inactive": "grey",
        "offline": "grey",
        "error": "negative",
        "failed": "negative",
        "warning": "warning",
        "pending": "warning",
    }

    colors = {**default_colors, **(color_map or {})}
    color = colors.get(status.lower(), "grey")

    return ui.badge(status.title(), color=color)
