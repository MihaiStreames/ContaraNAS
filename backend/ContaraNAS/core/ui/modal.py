from typing import ClassVar

from .base import Component


class Modal(Component):
    """Modal dialog"""

    _type: ClassVar[str] = "modal"

    id: str
    title: str
    children: list[Component] = []
    footer: list[Component] | None = None
    closable: bool = True
