import asyncio
import os

from nicegui import app, ui

import ContaraNAS.gui.factories  # This triggers register_all_components()
from ContaraNAS.core.module_manager import ModuleManager
from ContaraNAS.core.utils import get_logger
from ContaraNAS.gui.dashboard import DashboardView
from ContaraNAS.modules.steam import SteamModule

# Some fixes
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-gpu --no-sandbox"

logger = get_logger(__name__)

manager = ModuleManager()


def setup_modules():
    """Register all available modules with the manager"""
    logger.info("Registering modules...")

    # Register modules
    steam_module = SteamModule()
    manager.register(steam_module)

    logger.info(f"Registered {len(manager.modules)} modules")


async def restore_module_states():
    """Restore modules to their previous states"""
    logger.info("Restoring module states...")
    await manager.restore_module_states()


def setup_gui():
    """Setup the main GUI application"""
    logger.info("Setting up GUI...")

    ui.colors(primary="#1976d2")
    dashboard = DashboardView(manager)

    logger.info("GUI setup complete")


async def cleanup_on_shutdown():
    """Clean up all modules on app shutdown"""
    logger.info("ContaraNAS shutting down...")
    await manager.shutdown_all_modules()
    logger.info("Module cleanup complete")


def main():
    logger.info("Starting ContaraNAS...")

    # Setup components
    setup_modules()
    setup_gui()

    # Configure app
    app.on_startup(lambda: asyncio.create_task(restore_module_states()))
    app.on_shutdown(lambda: asyncio.create_task(cleanup_on_shutdown()))

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
