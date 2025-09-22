from dataclasses import dataclass
from typing import Any


@dataclass
class BaseTileViewModel:
    """Pure data object for tile display"""

    name: str
    enabled: bool
    status_text: str
    status_color: str
    tile_data: dict[str, Any]

    @classmethod
    def from_module_state(cls, name: str, module_state: dict[str, Any]) -> "BaseTileViewModel":
        """Factory method to create ViewModel from module state"""
        enabled = module_state.get("enabled", False)
        return cls(
            name=name,
            enabled=enabled,
            status_text="Running" if enabled else "Stopped",
            status_color="positive" if enabled else "grey",
            tile_data=module_state.get("tile_data", {}),
        )
