from abc import ABC, abstractmethod

from nicegui import ui

from src.core.module import Module
from src.core.utils import get_logger

logger = get_logger(__name__)


class ModuleDialog(ABC):
    """Abstract base class for module detail dialogs"""

    def __init__(self, name: str, module: Module):
        self.name = name
        self.module = module
        self.dialog = None

        # Create and show the dialog
        self._create_dialog()

    def _create_dialog(self):
        """Create the detail dialog."""
        with ui.dialog() as self.dialog:
            with ui.card().classes('w-[800px] max-h-[600px] p-4'):
                # Header
                with ui.row().classes('w-full items-center justify-between mb-4'):
                    ui.label(f"{self.name.title()} Details").classes('text-xl font-bold')
                    ui.button(
                        icon="close",
                        on_click=self.dialog.close
                    ).props('flat round')

                # Content scroll area
                with ui.column().classes('w-full max-h-96 overflow-auto'):
                    self._render_content()

        # Show the dialog
        self.dialog.open()

    def _render_content(self):
        """Render the detailed content based on module type."""
        try:
            detailed_data = self.module.get_detailed_data()
            self._render_details(detailed_data)

        except Exception as e:
            logger.error(f"Error rendering details for {self.name}: {e}")
            ui.label("Error loading module details").classes('text-red-500')

    @abstractmethod
    def _render_details(self, detailed_data: dict):
        """Render module-specific details. Must be implemented by subclasses"""
        pass

    @staticmethod
    def create_dialog(name: str, module: Module) -> 'ModuleDialog':
        """Factory method to create the appropriate dialog based on module type"""
        if module.name == "steam":
            from src.gui.components.steam.steam_dialog import SteamDialog
            return SteamDialog(name, module)
