import os
import src.gui.factories  # This triggers register_all_components()

from nicegui import ui, app

from core.module_manager import ModuleManager
from core.utils import get_logger
from modules.steam import SteamModule
from src.gui.dashboard import DashboardView

# Some fixes
os.environ['QTWEBENGINE_CHROMIUM_FLAGS'] = '--disable-gpu --no-sandbox'

logger = get_logger(__name__)

manager = ModuleManager()


def setup_modules():
    """Register all available modules with the manager"""
    logger.info("Registering modules...")

    # Register modules
    steam_module = SteamModule()
    manager.register(steam_module)

    logger.info(f"Registered {len(manager.modules)} modules")


def setup_gui():
    """Setup the main GUI application"""
    logger.info("Setting up GUI...")

    ui.colors(primary='#1976d2')
    dashboard = DashboardView(manager)

    logger.info("GUI setup complete")


def main():
    logger.info("Starting NAS Manager...")

    # Setup components
    setup_modules()
    setup_gui()

    # Configure app
    app.on_startup(lambda: logger.info("NAS Manager started successfully"))
    app.on_shutdown(lambda: logger.info("NAS Manager shutting down"))

    # Run the application
    ui.run(
        title="NAS Manager",
        native=True,
        window_size=(1200, 800),
        fullscreen=False,
        reload=False
    )


if __name__ == "__main__":
    main()
