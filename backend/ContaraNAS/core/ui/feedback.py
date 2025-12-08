from typing import ClassVar, Literal

from .base import Component


class Alert(Component):
    """Alert message"""

    _type: ClassVar[str] = "alert"

    message: str
    variant: Literal["info", "success", "warning", "error"] = "info"
    title: str | None = None


class Spinner(Component):
    """Loading spinner"""

    _type: ClassVar[str] = "spinner"

    size: Literal["sm", "md", "lg"] = "md"
    label: str | None = None
