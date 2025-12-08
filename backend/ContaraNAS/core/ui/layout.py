from typing import ClassVar, Literal

from .base import Component


class Stack(Component):
    """Flex container for vertical or horizontal layouts"""

    _type: ClassVar[str] = "stack"

    direction: Literal["horizontal", "vertical"] = "vertical"
    gap: Literal["0", "1", "2", "3", "4", "5", "6", "8"] = "4"
    align: Literal["start", "center", "end", "stretch"] = "stretch"
    justify: Literal["start", "center", "end", "between", "around"] = "start"
    children: list[Component] = []


class Grid(Component):
    """CSS Grid layout"""

    _type: ClassVar[str] = "grid"

    columns: int | str = 2  # number or template string
    gap: Literal["0", "1", "2", "3", "4", "5", "6", "8"] = "4"
    children: list[Component] = []
