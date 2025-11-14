import asyncio
from collections.abc import Callable
import contextlib

from ContaraNAS.core.utils import get_logger


logger = get_logger(__name__)


class SysMonitorMonitoringService:
    """Service for periodic system monitoring updates"""

    def __init__(self, update_callback: Callable, interval: float = 2.0):
        self.update_callback = update_callback
        self.interval = interval
        self.monitor_flag = False
        self._task: asyncio.Task | None = None

    async def start_monitoring(self) -> None:
        """Start periodic system monitoring"""
        if self.monitor_flag:
            logger.debug("Monitoring already started")
            return

        logger.info(f"Starting system monitoring with {self.interval}s interval...")

        self.monitor_flag = True
        self._task = asyncio.create_task(self._monitoring_loop())

        logger.info("System monitoring started")

    async def stop_monitoring(self) -> None:
        """Stop periodic system monitoring"""
        if not self.monitor_flag:
            logger.debug("Monitoring already stopped")
            return

        logger.info("Stopping system monitoring...")

        self.monitor_flag = False
        if self._task:
            self._task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._task
            self._task = None

        logger.info("System monitoring stopped")

    async def _monitoring_loop(self) -> None:
        """Background loop that polls system stats periodically"""
        while self.monitor_flag:
            try:
                # Call the update callback to collect and update stats
                await self.update_callback()
                await asyncio.sleep(self.interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(self.interval)
