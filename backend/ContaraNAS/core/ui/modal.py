from typing import ClassVar
from typing import Literal

from .base import Component


class Modal(Component):
    """Modal dialog"""

    _type: ClassVar[str] = "modal"

    id: str
    title: str
    size: Literal["sm", "md", "lg", "xl"] = "md"
    children: list[Component] = []
    footer: list[Component] | None = None
    closable: bool = True
