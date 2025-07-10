from core.module import Module
from core.utils import get_logger
from nicegui import ui

logger = get_logger(__name__)


class ModuleDetailDialog:
    """Dialog for displaying detailed module information"""

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
            # TODO: Render specific details based on module type (via OOP)
            pass

        except Exception as e:
            logger.error(f"Error rendering details for {self.name}: {e}")
            ui.label("Error loading module details").classes('text-red-500')
