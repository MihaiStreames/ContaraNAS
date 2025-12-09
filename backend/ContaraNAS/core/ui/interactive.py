from collections.abc import Callable
from typing import ClassVar, Literal

from .base import Component


class Button(Component):
    """Clickable button"""

    _type: ClassVar[str] = "button"

    label: str
    on_click: Callable | None = None
    variant: Literal["primary", "secondary", "ghost", "danger"] = "primary"
    size: Literal["sm", "md", "lg"] = "md"
    icon: str | None = None
    icon_only: bool = False  # True for btn-icon-only style
    disabled: bool = False
    loading: bool = False


class Input(Component):
    """Text input field"""

    _type: ClassVar[str] = "input"

    name: str
    label: str | None = None
    value: str = ""
    input_type: Literal["text", "password", "email", "number"] = "text"
    placeholder: str | None = None
    disabled: bool = False


class SelectOption(Component):
    """Option for Select component"""

    _type: ClassVar[str] = "select_option"

    value: str
    label: str


class Select(Component):
    """Dropdown select"""

    _type: ClassVar[str] = "select"

    name: str
    label: str | None = None
    options: list[SelectOption]
    value: str | None = None
    disabled: bool = False


class Toggle(Component):
    """Toggle switch"""

    _type: ClassVar[str] = "toggle"

    name: str
    label: str | None = None
    checked: bool = False
    disabled: bool = False


class Checkbox(Component):
    """Checkbox input"""

    _type: ClassVar[str] = "checkbox"

    name: str
    label: str | None = None
    checked: bool = False
    disabled: bool = False


class Tab(Component):
    """Single tab within Tabs component"""

    _type: ClassVar[str] = "tab"

    id: str
    label: str
    icon: str | None = None
    children: list[Component] = []


class Tabs(Component):
    """Tab container with switchable content panels"""

    _type: ClassVar[str] = "tabs"

    tabs: list["Tab"]
    default_tab: str | None = None  # Tab id to show by default
    size: Literal["sm", "md"] = "md"
