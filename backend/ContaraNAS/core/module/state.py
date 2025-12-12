from collections.abc import Callable
from typing import Any

import msgspec
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import PrivateAttr


class ModuleState(BaseModel):
    """Base class for typed module state with dirty tracking"""

    model_config = ConfigDict(
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    _dirty: bool = PrivateAttr(default=False)
    _on_commit: Callable[[], Any] | None = PrivateAttr(default=None)
    _last_committed: dict[str, Any] | None = PrivateAttr(default=None)

    def model_post_init(self, __context: Any) -> None:
        self._last_committed = self._serialize()

    def __setattr__(self, name: str, value: Any) -> None:
        if name.startswith("_"):
            object.__setattr__(self, name, value)
            return

        if name in type(self).model_fields:
            try:
                old_value = getattr(self, name, None)
                if old_value != value:
                    self._dirty = True
            except AttributeError:
                pass

        super().__setattr__(name, value)

    @property
    def is_dirty(self) -> bool:
        """Check if state has unsaved changes"""
        return self._dirty

    def mark_dirty(self) -> None:
        """Manually mark state as dirty"""
        self._dirty = True

    def commit(self) -> None:
        """Signal that current state should be pushed to frontend"""
        if self._on_commit is not None:
            self._on_commit()

        self._last_committed = self._serialize()
        self._dirty = False

    def set_commit_callback(self, callback: Callable[[], Any]) -> None:
        """Set callback to be called on commit"""
        self._on_commit = callback

    def _serialize_value(self, value: Any) -> Any:
        """Recursively serialize a value, handling msgspec Structs and collections"""
        if isinstance(value, msgspec.Struct):
            return msgspec.to_builtins(value)
        if isinstance(value, (list, tuple)):
            return [self._serialize_value(v) for v in value]
        if (
            hasattr(value, "__iter__")
            and hasattr(value, "append")
            and not isinstance(value, (str, bytes, dict))
        ):
            return [self._serialize_value(v) for v in value]
        if isinstance(value, dict):
            return {k: self._serialize_value(v) for k, v in value.items()}
        if isinstance(value, BaseModel):
            return value.model_dump(mode="json")

        return value

    def _serialize(self) -> dict[str, Any]:
        """Serialize state to dictionary"""
        result = {}

        for field_name in type(self).model_fields:
            value = getattr(self, field_name)
            result[field_name] = self._serialize_value(value)

        return result

    def to_dict(self) -> dict[str, Any]:
        """Convert state to dictionary"""
        return self._serialize()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ModuleState":
        """Create state from dictionary"""
        return cls.model_validate(data)

    def get_changes(self) -> dict[str, Any] | None:
        """Get fields that changed since last commit"""
        if not self._dirty or self._last_committed is None:
            return None

        current = self._serialize()
        changes = {
            key: value
            for key, value in current.items()
            if key not in self._last_committed or self._last_committed[key] != value
        }

        return changes if changes else None

    def reset(self) -> None:
        """Reset state to default values"""
        fields = type(self).model_fields

        for field_name, field_info in fields.items():
            if field_info.default is not None:
                setattr(self, field_name, field_info.default)
            elif field_info.default_factory is not None:
                setattr(self, field_name, field_info.default_factory())

        self._dirty = True
