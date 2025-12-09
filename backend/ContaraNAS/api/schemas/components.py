from typing import Annotated, Any, Literal

from pydantic import BaseModel, Field


class ActionRef(BaseModel):
    """Reference to a callable action"""

    model_config = {"populate_by_name": True}

    action: str = Field(..., serialization_alias="__action__", validation_alias="__action__")
    params: dict[str, Any] | None = Field(
        default=None, serialization_alias="__params__", validation_alias="__params__"
    )


class StackSchema(BaseModel):
    """Flex container for vertical or horizontal layouts"""

    type: Literal["stack"] = "stack"
    direction: Literal["horizontal", "vertical"] = "vertical"
    gap: Literal["0", "1", "2", "3", "4", "5", "6", "8"] = "4"
    align: Literal["start", "center", "end", "stretch"] = "stretch"
    justify: Literal["start", "center", "end", "between", "around"] = "start"
    children: list["ComponentSchema"] = []


class GridSchema(BaseModel):
    """CSS Grid layout"""

    type: Literal["grid"] = "grid"
    columns: int | str = 2
    gap: Literal["0", "1", "2", "3", "4", "5", "6", "8"] = "4"
    children: list["ComponentSchema"] = []


class StatSchema(BaseModel):
    """Inline stat display (value + label) for tiles"""

    type: Literal["stat"] = "stat"
    label: str
    value: str | int | float


class BadgeSchema(BaseModel):
    """Small label badge"""

    type: Literal["badge"] = "badge"
    text: str
    variant: Literal["default", "primary", "success", "warning", "error", "info"] = "default"


class CardSchema(BaseModel):
    """Card container with optional header and footer"""

    type: Literal["card"] = "card"
    icon: str | None = None
    title: str | None = None
    children: list["ComponentSchema"] = []
    footer: list["ComponentSchema"] | None = None


class TileSchema(BaseModel):
    """Module tile - specialized card for dashboard modules"""

    type: Literal["tile"] = "tile"
    icon: str
    title: str
    colspan: Literal[1, 2, 3] = 1
    badge: BadgeSchema | None = None
    stats: list[StatSchema] = []
    content: list["ComponentSchema"] | None = None
    actions: list["ComponentSchema"] = []


class TextSchema(BaseModel):
    """Text with styling variants"""

    type: Literal["text"] = "text"
    content: str
    variant: Literal["body", "secondary", "muted", "code"] = "body"


class StatCardSchema(BaseModel):
    """Standalone stat card with icon and optional trend"""

    type: Literal["stat_card"] = "stat_card"
    label: str
    value: str | int | float
    icon: str | None = None
    color: Literal["default", "success", "warning", "error"] = "default"
    trend: tuple[Literal["up", "down"], str] | None = None


class ProgressSchema(BaseModel):
    """Progress bar with optional labels"""

    type: Literal["progress"] = "progress"
    value: int | float
    max: int | float = 100
    label: str | None = None
    sublabel: str | None = None
    color: Literal["default", "success", "warning", "error"] = "default"
    size: Literal["sm", "lg"] = "sm"


class TableColumnSchema(BaseModel):
    """Column definition for Table"""

    type: Literal["table_column"] = "table_column"
    key: str
    label: str
    width: str | None = None
    align: Literal["left", "center", "right"] = "left"


class TableSchema(BaseModel):
    """Data table"""

    type: Literal["table"] = "table"
    columns: list[TableColumnSchema]
    data: list[dict[str, Any]]
    empty_message: str = "No data"


class ButtonSchema(BaseModel):
    """Clickable button"""

    type: Literal["button"] = "button"
    label: str
    on_click: ActionRef | None = None
    variant: Literal["primary", "secondary", "ghost", "danger"] = "primary"
    size: Literal["sm", "md", "lg"] = "md"
    icon: str | None = None
    icon_only: bool = False
    disabled: bool = False
    loading: bool = False


class InputSchema(BaseModel):
    """Text input field"""

    type: Literal["input"] = "input"
    name: str
    label: str | None = None
    value: str = ""
    input_type: Literal["text", "password", "email", "number"] = "text"
    placeholder: str | None = None
    disabled: bool = False


class SelectOptionSchema(BaseModel):
    """Option for Select component"""

    type: Literal["select_option"] = "select_option"
    value: str
    label: str


class SelectSchema(BaseModel):
    """Dropdown select"""

    type: Literal["select"] = "select"
    name: str
    label: str | None = None
    options: list[SelectOptionSchema]
    value: str | None = None
    disabled: bool = False


class ToggleSchema(BaseModel):
    """Toggle switch"""

    type: Literal["toggle"] = "toggle"
    name: str
    label: str | None = None
    checked: bool = False
    disabled: bool = False


class CheckboxSchema(BaseModel):
    """Checkbox input"""

    type: Literal["checkbox"] = "checkbox"
    name: str
    label: str | None = None
    checked: bool = False
    disabled: bool = False


class ModalSchema(BaseModel):
    """Modal dialog"""

    type: Literal["modal"] = "modal"
    id: str
    title: str
    size: Literal["sm", "md", "lg", "xl"] = "md"
    children: list["ComponentSchema"] = []
    footer: list["ComponentSchema"] | None = None
    closable: bool = True


class AlertSchema(BaseModel):
    """Alert message"""

    type: Literal["alert"] = "alert"
    message: str
    variant: Literal["info", "success", "warning", "error"] = "info"
    title: str | None = None


class SpinnerSchema(BaseModel):
    """Loading spinner"""

    type: Literal["spinner"] = "spinner"
    size: Literal["sm", "md", "lg"] = "md"
    label: str | None = None


class SegmentedProgressSegmentSchema(BaseModel):
    """Segment for SegmentedProgress bar"""

    type: Literal["segment"] = "segment"
    value: int | float
    color: str  # CSS color or semantic: "primary", "success", etc.
    label: str | None = None  # Tooltip/legend label


class SegmentedProgressSchema(BaseModel):
    """Progress bar with multiple colored segments"""

    type: Literal["segmented_progress"] = "segmented_progress"
    segments: list[SegmentedProgressSegmentSchema]
    max: int | float = 100
    size: Literal["sm", "lg"] = "sm"
    show_legend: bool = False


class LineChartSchema(BaseModel):
    """Simple line chart for time-series data"""

    type: Literal["line_chart"] = "line_chart"
    data: list[float]  # Y values, rendered left-to-right
    max: float = 100
    min: float = 0
    height: int = 80  # px
    color: Literal["default", "primary", "success", "warning", "error"] = "primary"
    fill: bool = True  # Fill area under line
    label: str | None = None  # Current value label overlay


class TabSchema(BaseModel):
    """Single tab within Tabs component"""

    type: Literal["tab"] = "tab"
    id: str
    label: str
    icon: str | None = None
    children: list["ComponentSchema"] = []


class TabsSchema(BaseModel):
    """Tab container with switchable content panels"""

    type: Literal["tabs"] = "tabs"
    tabs: list[TabSchema]
    default_tab: str | None = None  # Tab id to show by default
    size: Literal["sm", "md"] = "md"


ComponentSchema = Annotated[
    StackSchema
    | GridSchema
    | CardSchema
    | TileSchema
    | StatSchema
    | TextSchema
    | StatCardSchema
    | ProgressSchema
    | SegmentedProgressSchema
    | SegmentedProgressSegmentSchema
    | LineChartSchema
    | BadgeSchema
    | TableSchema
    | TableColumnSchema
    | ButtonSchema
    | InputSchema
    | SelectSchema
    | SelectOptionSchema
    | ToggleSchema
    | CheckboxSchema
    | TabsSchema
    | TabSchema
    | ModalSchema
    | AlertSchema
    | SpinnerSchema,
    Field(discriminator="type"),
]


# Update forward references for recursive types
StackSchema.model_rebuild()
GridSchema.model_rebuild()
CardSchema.model_rebuild()
TileSchema.model_rebuild()
ModalSchema.model_rebuild()
TabSchema.model_rebuild()
TabsSchema.model_rebuild()
