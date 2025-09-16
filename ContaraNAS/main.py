import asyncio
import os

from nicegui import app, ui

from ContaraNAS.gui.factories import register_all_components # This triggers register_all_components()
from ContaraNAS.core.module_manager import ModuleManager
from ContaraNAS.core.utils import get_logger
from ContaraNAS.gui.dashboard import DashboardView

# Some fixes
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-gpu --no-sandbox"

logger = get_logger(__name__)

def setup_gui(manager: ModuleManager):
    """Setup the main GUI application"""
    logger.info("Setting up GUI...")

    ui.colors(primary="#1976d2")
    dashboard = DashboardView(manager)

    logger.info("GUI setup complete")


async def cleanup_on_shutdown(manager: ModuleManager):
    """Clean up all modules on app shutdown"""
    logger.info("ContaraNAS shutting down, cleaning up modules...")

    for name, module in manager.modules.items():
        if module.enable_flag:
            try:
                await module.disable()
                logger.info(f"Disabled module: {name}")
            except Exception as e:
                logger.error(f"Error disabling module {name}: {e}")

    logger.info("Module cleanup complete")


def main():
    logger.info("Starting ContaraNAS...")
    
    # Setup components
    register_all_components()
    manager = ModuleManager()
    setup_gui(manager=manager)

    # Configure app
    app.on_startup(lambda: logger.info("ContaraNAS started successfully"))
    app.on_shutdown(lambda: asyncio.create_task(cleanup_on_shutdown(manager)))

    # Run the application
    ui.run(
        title="ContaraNAS",
        native=True,
        window_size=(1200, 800),
        fullscreen=False,
        reload=False,
    )


if __name__ == "__main__":
    main()
