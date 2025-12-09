from typing import Any, ClassVar, Literal

from .base import Component


class Text(Component):
    """Text with styling variants"""

    _type: ClassVar[str] = "text"

    content: str
    variant: Literal["body", "secondary", "muted", "code"] = "body"
    size: Literal["sm", "base", "lg", "xl"] = "base"


class StatSmall(Component):
    """Compact inline stat with label and value side by side"""

    _type: ClassVar[str] = "stat_small"

    label: str
    value: str | int | float


class StatCard(Component):
    """Standalone stat card with icon and optional trend"""

    _type: ClassVar[str] = "stat_card"

    label: str
    value: str | int | float
    icon: str | None = None
    color: Literal["default", "success", "warning", "error"] = "default"
    trend: tuple[Literal["up", "down"], str] | None = None  # (direction, value)


class Progress(Component):
    """Progress bar with optional labels"""

    _type: ClassVar[str] = "progress"

    value: int | float
    max: int | float = 100
    label: str | None = None
    sublabel: str | None = None  # e.g. "743 GB used"
    color: Literal["default", "success", "warning", "error"] = "default"
    size: Literal["sm", "lg"] = "sm"


class Badge(Component):
    """Small label badge"""

    _type: ClassVar[str] = "badge"

    text: str
    variant: Literal["default", "primary", "success", "warning", "error", "info"] = "default"


class TableColumn(Component):
    """Column definition for Table"""

    _type: ClassVar[str] = "table_column"

    key: str
    label: str
    width: str | None = None
    align: Literal["left", "center", "right"] = "left"
    render: Literal["text", "image"] = "text"  # How to render cell values
    sortable: bool = True  # Whether this column can be sorted


class Table(Component):
    """Data table"""

    _type: ClassVar[str] = "table"

    columns: list[TableColumn]
    data: list[dict[str, Any]]
    empty_message: str = "No data"
    sortable: bool = False  # Enable column sorting
    default_sort_key: str | None = None  # Column key to sort by initially
    default_sort_desc: bool = True  # Sort descending by default


class SegmentedProgressSegment(Component):
    """Segment for SegmentedProgress bar"""

    _type: ClassVar[str] = "segment"

    value: int | float
    color: str  # CSS color or semantic: "primary", "success", "warning", "error", "info"
    label: str | None = None  # Tooltip/legend label


class SegmentedProgress(Component):
    """Progress bar with multiple colored segments"""

    _type: ClassVar[str] = "segmented_progress"

    segments: list[SegmentedProgressSegment]
    max: int | float = 100
    size: Literal["sm", "lg"] = "sm"
    show_legend: bool = False


class LineChart(Component):
    """Simple line chart for time-series data"""

    _type: ClassVar[str] = "line_chart"

    data: list[float]  # Y values, rendered left-to-right
    max: float = 100
    min: float = 0
    height: int = 80  # px
    color: Literal["default", "primary", "success", "warning", "error"] = "primary"
    fill: bool = True  # Fill area under line
    label: str | None = None  # Current value label overlay


class Image(Component):
    """Image display component"""

    _type: ClassVar[str] = "image"

    src: str  # Image URL
    alt: str = ""  # Alt text for accessibility
    width: int | None = None  # Width in pixels
    height: int | None = None  # Height in pixels
    border_radius: Literal["none", "sm", "md", "lg"] = "sm"
