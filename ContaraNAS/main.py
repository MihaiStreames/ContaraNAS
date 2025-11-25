import asyncio
import os

from ContaraNAS.core.module_manager import ModuleManager
from ContaraNAS.core.utils import get_logger

# Some fixes
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-gpu --no-sandbox"

logger = get_logger(__name__)


async def restore_module_states(manager: ModuleManager):
    """Restore modules to their previous states"""
    logger.info("Restoring module states...")
    await manager.restore_module_states()


def setup_gui(manager: ModuleManager):
    """Setup the main GUI application"""
    logger.info("Setting up GUI...")

    # Restore module states after UI is ready (using timer for native mode)
    # ui.timer(0.1, lambda: asyncio.create_task(restore_module_states(manager)), once=True)

    logger.info("GUI setup complete")


async def cleanup_on_shutdown(manager: ModuleManager):
    """Clean up all modules on app shutdown"""
    logger.info("ContaraNAS shutting down...")
    await manager.shutdown_all_modules()
    logger.info("Module cleanup complete")


def main():
    logger.info("Starting ContaraNAS...")

    # Setup components
    manager = ModuleManager()
    setup_gui(manager=manager)

    # Configure app shutdown handler
    # app.on_shutdown(lambda: asyncio.create_task(cleanup_on_shutdown(manager)))


if __name__ == "__main__":
    main()
