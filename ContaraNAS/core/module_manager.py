from importlib.metadata import entry_points
from typing import Any

from ContaraNAS.core.module import Module
from ContaraNAS.core.state_manager import state_manager
from ContaraNAS.core.utils import get_logger


logger = get_logger(__name__)


class ModuleManager:
    """Central manager for all system modules"""

    def __init__(self) -> None:
        self.modules: dict[str, Module] = {}
        self.discover_modules()

    def discover_modules(self):
        """Discover and load modules via entry points"""
        try:
            discovered = entry_points(group="contaranas.modules")
            for entry_point in discovered:
                try:
                    module_class = entry_point.load()
                    instance = module_class()
                    self.register(instance)
                    logger.info(f"Loaded module: {entry_point.name}")
                except Exception as e:
                    logger.error(f"Failed to load {entry_point.name}: {e}")
        except Exception as e:
            logger.warning(f"No modules found: {e}")

    def register(self, module: Module):
        """Register a module"""
        self.modules[module.name] = module
        logger.info(f"Registered module: {module.name}")

    async def enable_module(self, name: str) -> None:
        """Enable a registered module"""
        if name in self.modules:
            await self.modules[name].enable()
            state_manager.mark_enabled(name)

    async def disable_module(self, name: str) -> None:
        """Disable a registered module"""
        if name in self.modules:
            await self.modules[name].disable()
            state_manager.mark_disabled(name)

    async def restore_module_states(self) -> None:
        """Restore modules to their previous states on startup"""
        enabled_modules = state_manager.get_enabled_modules()

        if not enabled_modules:
            logger.info("No modules to restore")
            return

        logger.info(f"Restoring {len(enabled_modules)} modules: {list(enabled_modules)}")

        # Enable modules that were previously enabled
        for module_name in enabled_modules:
            if module_name in self.modules:
                try:
                    await self.enable_module(module_name)
                    logger.info(f"Restored module: {module_name}")
                except Exception as e:
                    logger.error(f"Failed to restore module '{module_name}': {e}")
                    # Remove from enabled list if it fails to start
                    state_manager.mark_disabled(module_name)
            else:
                logger.warning(f"Module '{module_name}' was enabled but is no longer registered")
                # Clean up state for non-existent modules
                state_manager.mark_disabled(module_name)

    async def shutdown_all_modules(self) -> None:
        """Disable all currently enabled modules during shutdown"""
        logger.info("Shutting down all modules...")

        for name, module in self.modules.items():
            if module.enable_flag:
                try:
                    await module.disable()
                    logger.info(f"Shutdown module: {name}")
                except Exception as e:
                    logger.error(f"Error shutting down module {name}: {e}")

    def get_module_state(self, module_name: str) -> dict[str, Any] | None:
        """Get current state of a specific module"""
        if module_name not in self.modules:
            return None

        module = self.modules[module_name]
        return {
            "name": module_name,
            "display_name": module.display_name,
            "enabled": module.enable_flag,
            "initialized": module.init_flag,
            "state": module.state.copy(),
            "tile_data": module.get_tile_data(),
        }

    def get_all_states(self) -> dict[str, dict[str, Any] | None]:
        """Get states of all modules"""
        return {name: self.get_module_state(name) for name in self.modules}
