from typing import Any
from typing import ClassVar
from typing import Literal

from pydantic import BaseModel


class ActionResult(BaseModel):
    """Base class for action results"""

    _type: ClassVar[str] = "result"

    def to_dict(self) -> dict[str, Any]:
        """Serialize result to dictionary"""
        return {"type": self._type, **{name: value for name, value in self if value is not None}}


class OpenModal(ActionResult):
    """Signal to open a modal"""

    _type: ClassVar[str] = "open_modal"

    modal_id: str


class CloseModal(ActionResult):
    """Signal to close a modal"""

    _type: ClassVar[str] = "close_modal"

    modal_id: str | None = None  # None closes the currently open modal


class Notify(ActionResult):
    """Show a notification"""

    _type: ClassVar[str] = "notify"

    message: str
    variant: Literal["info", "success", "warning", "error"] = "info"
    title: str | None = None


class Refresh(ActionResult):
    """Force a UI refresh"""

    _type: ClassVar[str] = "refresh"
