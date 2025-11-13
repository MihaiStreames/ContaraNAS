from typing import Any

from ContaraNAS.core.module import Module
from ContaraNAS.core.utils import get_logger


logger = get_logger(__name__)


class SysMonitorModule(Module):
    """Module for monitoring your NAS system"""

    def __init__(self) -> None:
        # controller later on
        super().__init__("sys_monitor")

    async def initialize(self) -> None:
        """Initialize the SysMonitor module"""
        # self.controller = ...
        # self.controller.initialize()

    async def start_monitoring(self) -> None:
        """Start System monitoring"""
        # self.controller.start_monitoring()
        logger.info("Steam monitoring started")

    async def stop_monitoring(self) -> None:
        """Stop System monitoring"""
        # self.controller.stop_monitoring()
        logger.info("Steam monitoring stopped")

    def get_tile_data(self) -> dict[str, Any]:
        """Get data for dashboard tile"""
        # return self.controller.get_tile_data()
