from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class BaseTileViewModel:
    """Pure data object for tile display"""
    name: str
    enabled: bool
    status_text: str
    status_color: str
    tile_data: Dict[str, Any]

    @classmethod
    def from_module_state(cls, name: str, module_state: Dict[str, Any]) -> 'BaseTileViewModel':
        """Factory method to create ViewModel from module state"""
        enabled = module_state.get('enabled', False)
        return cls(
            name=name,
            enabled=enabled,
            status_text="Running" if enabled else "Stopped",
            status_color="positive" if enabled else "grey",
            tile_data=module_state.get('tile_data', {})
        )
