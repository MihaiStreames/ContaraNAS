from typing import Annotated, Any, Literal

from pydantic import BaseModel, Field


class ActionRef(BaseModel):
    """Reference to a callable action"""

    model_config = {"populate_by_name": True}

    action: str = Field(..., serialization_alias="__action__", validation_alias="__action__")


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


ComponentSchema = Annotated[
    StackSchema
    | GridSchema
    | CardSchema
    | TileSchema
    | StatSchema
    | TextSchema
    | StatCardSchema
    | ProgressSchema
    | BadgeSchema
    | TableSchema
    | TableColumnSchema
    | ButtonSchema
    | InputSchema
    | SelectSchema
    | SelectOptionSchema
    | ToggleSchema
    | CheckboxSchema
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
