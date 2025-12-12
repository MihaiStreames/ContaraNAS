from collections.abc import Callable
from typing import Any

from ContaraNAS.core.logger import get_logger
from ContaraNAS.core.module import Module
from ContaraNAS.core.state_manager import state_manager


logger = get_logger(__name__)


class ModuleManager:
    """Central manager for all system modules"""

    def _discover_and_register(self) -> None:
        """Discover and register all available modules"""
        discovered = self._loader.discover()

        for module_id, (metadata, _) in discovered.items():
            try:
                module_class = self._loader.load_module_class(module_id)

                instance = module_class(
                    name=metadata.id,
                    display_name=metadata.name,
                    metadata=metadata,
                )

                self.modules[module_id] = instance

                logger.info(f"Registered module: {module_id} v{metadata.version}")

            except Exception as e:
                logger.error(f"Failed to register {module_id}: {e}")

    def __init__(self) -> None:
        # Delay import to avoid circular dependency
        from ContaraNAS.modules import module_loader

        self._loader = module_loader
        self.modules: dict[str, Module] = {}
        self._discover_and_register()

    def set_ui_update_callback(self, callback: Callable[[Module], None]) -> None:
        """Set UI update callback on all modules"""
        for module in self.modules.values():
            module.set_ui_update_callback(callback)

    async def enable_module(self, name: str) -> None:
        """Enable a module and persist the state"""
        if name not in self.modules:
            raise KeyError(f"Module '{name}' is not registered")

        await self.modules[name].enable()
        state_manager.mark_enabled(name)
        logger.info(f"Enabled module: {name}")

    async def disable_module(self, name: str) -> None:
        """Disable a module and persist the state"""
        if name not in self.modules:
            raise KeyError(f"Module '{name}' is not registered")

        await self.modules[name].disable()
        state_manager.mark_disabled(name)
        logger.info(f"Disabled module: {name}")

    async def restore_module_states(self) -> None:
        """Restore modules to their previous enabled/disabled states"""
        enabled_modules = state_manager.get_enabled_modules()

        if not enabled_modules:
            logger.info("No modules to restore")
            return

        logger.info(f"Restoring {len(enabled_modules)} modules")

        for module_name in enabled_modules:
            if module_name not in self.modules:
                logger.warning(f"Module '{module_name}' no longer exists")
                state_manager.mark_disabled(module_name)
                continue

            try:
                await self.enable_module(module_name)

            except Exception as e:
                logger.error(f"Failed to restore '{module_name}': {e}")
                state_manager.mark_disabled(module_name)

    async def shutdown_all_modules(self) -> None:
        """Gracefully disable all currently enabled modules"""
        logger.info("Shutting down all modules...")

        for name, module in self.modules.items():
            if module.enable_flag:
                try:
                    await module.disable()

                except Exception as e:
                    logger.error(f"Error shutting down {name}: {e}")

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
            "ui": module.render_ui() if module.enable_flag else None,
        }

    def get_all_states(self) -> dict[str, dict | None]:
        """Get states of all modules"""
        return {name: self.get_module_state(name) for name in self.modules}
