from datetime import datetime
from typing import Any

from ContaraNAS.core.utils import get_logger
from ContaraNAS.modules.sys_monitor.services.cpu_service import CPUService
from ContaraNAS.modules.sys_monitor.services.disk_service import DiskService
from ContaraNAS.modules.sys_monitor.services.mem_service import MemService
from ContaraNAS.modules.sys_monitor.services.monitoring_service import (
    SysMonitorMonitoringService,
)


logger = get_logger(__name__)


class SysMonitorController:
    """Controller that orchestrates System Monitor module operations"""

    def __init__(self, state_update_callback, update_interval: float = 2.0):
        self.state_update_callback = state_update_callback
        self.monitor_flag = False
        self.update_interval = update_interval

        # Initialize services
        self.cpu_service = CPUService()
        self.mem_service = MemService()
        self.disk_service = DiskService()
        self.monitoring_service = SysMonitorMonitoringService(
            self._collect_and_update_stats, interval=update_interval
        )

    async def initialize(self) -> None:
        """Initialize the controller and its services"""
        logger.info("Initializing System Monitor controller...")

        # Perform initial data collection
        await self.state_update_callback(
            initialized_at=datetime.now(),
        )

        logger.info("System Monitor controller initialized successfully")

    async def start_monitoring(self) -> None:
        """Start monitoring system stats"""
        if self.monitor_flag:
            logger.debug("Monitoring already started")
            return

        await self.monitoring_service.start_monitoring()
        self.monitor_flag = True

    async def stop_monitoring(self) -> None:
        """Stop monitoring system stats"""
        if not self.monitor_flag:
            logger.debug("Monitoring already stopped")
            return

        await self.monitoring_service.stop_monitoring()
        self.monitor_flag = False

    async def _collect_and_update_stats(self) -> None:
        """Collect all system stats and update module state"""
        try:
            # Collect data from all services
            cpu_info = self.cpu_service.get_cpu_info()
            mem_info = self.mem_service.get_memory_info()
            disk_info = self.disk_service.get_disk_info()

            # Update module state (this triggers event emission to GUI)
            await self.state_update_callback(
                last_update=datetime.now(),
                cpu=cpu_info,
                memory=mem_info,
                disks=disk_info,
            )

        except Exception as e:
            logger.error(f"Error collecting system stats: {e}")

    async def get_tile_data(self) -> dict[str, Any]:
        """Build tile data for display"""
        # Get fresh data for tile display
        try:
            cpu_info = self.cpu_service.get_cpu_info()
            mem_info = self.mem_service.get_memory_info()
            disk_info = self.disk_service.get_disk_info()

            return {
                "cpu": cpu_info,
                "memory": mem_info,
                "disks": disk_info,
            }
        except Exception as e:
            logger.error(f"Error getting tile data: {e}")
            return {}
