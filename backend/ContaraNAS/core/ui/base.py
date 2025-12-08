from collections.abc import Callable
from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict


class Component(BaseModel):
    """Base class for all UI components"""

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra="forbid",
    )

    # Component type name, set by subclasses
    _type: ClassVar[str] = "component"

    def to_dict(self) -> dict[str, Any]:
        """Serialize component to dictionary for frontend"""
        data: dict[str, Any] = {"type": self._type}

        for name, value in self:
            if value is None:
                continue
            data[name] = self._serialize_value(value)

        return data

    def _serialize_value(self, value: Any) -> Any:
        """Serialize a value, handling special types"""
        if isinstance(value, Component):
            return value.to_dict()
        if isinstance(value, list):
            return [self._serialize_value(v) for v in value]
        if isinstance(value, dict):
            return {k: self._serialize_value(v) for k, v in value.items()}
        if callable(value):
            return self._serialize_action(value)
        return value

    def _serialize_action(self, func: Callable) -> dict[str, Any]:
        """Serialize a callable action reference"""
        # Action serialization will be handled by ActionDispatcher in Phase 3
        action_name = getattr(func, "__action_name__", None)
        if action_name:
            return {"__action__": action_name}

        if hasattr(func, "__name__"):
            return {"__action__": func.__name__}

        return {"__action__": "unknown"}
