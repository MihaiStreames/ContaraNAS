from __future__ import annotations

from typing import ClassVar

from .base import Component


class Stat(Component):
    """Inline stat display (value + label) for tiles"""

    _type: ClassVar[str] = "stat"

    label: str
    value: str | int | float


class Card(Component):
    """Card container with optional header and footer"""

    _type: ClassVar[str] = "card"

    icon: str | None = None
    title: str | None = None
    children: list[Component] = []
    footer: list[Component] | None = None


class Tile(Component):
    """Module tile - specialized card for dashboard modules"""

    _type: ClassVar[str] = "tile"

    icon: str
    title: str
    colspan: int = 1  # Number of columns to span (1, 2, or 3)
    rowspan: int = 1  # Number of rows to span (1, 2, or 3)
    stats: list[Stat] = []
    content: list[Component] | None = None  # Alternative to stats (e.g., progress bar)
    actions: list[Component] = []
