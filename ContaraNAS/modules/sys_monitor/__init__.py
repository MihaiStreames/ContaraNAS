from typing import Any

from ContaraNAS.core.module import Module
from ContaraNAS.core.utils import get_logger
from ContaraNAS.modules.sys_monitor.controllers.sys_monitor_controller import (
    SysMonitorController,
)


logger = get_logger(__name__)


class SysMonitorModule(Module):
    """Module for monitoring your NAS system"""

    def __init__(self) -> None:
        self.controller: SysMonitorController | None = None
        super().__init__("sys_monitor", display_name="System Monitor")

    async def initialize(self) -> None:
        """Initialize the SysMonitor module"""
        self.controller = SysMonitorController(self.update_state, update_interval=2.0)
        await self.controller.initialize()

    async def start_monitoring(self) -> None:
        """Start System monitoring"""
        if self.controller:
            await self.controller.start_monitoring()
            logger.info("System monitoring started")

    async def stop_monitoring(self) -> None:
        """Stop System monitoring"""
        if self.controller:
            await self.controller.cleanup()
            logger.info("System monitoring stopped")

    async def get_tile_data(self) -> dict[str, Any]:
        """Get data for dashboard tile"""
        if not self.controller:
            return {"error": "Module not initialized"}

        return await self.controller.get_tile_data()
