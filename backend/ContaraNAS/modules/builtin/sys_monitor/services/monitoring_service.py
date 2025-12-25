import asyncio
from collections.abc import Awaitable
from collections.abc import Callable
import contextlib

from ContaraNAS.core import get_logger


logger = get_logger(__name__)


class SysMonitorMonitoringService:
    """Service for periodic system monitoring updates"""

    def __init__(self, update_callback: Callable[[], Awaitable[None]], interval: float = 2.0):
        self._update_callback: Callable[[], Awaitable[None]] = update_callback
        self._interval: float = interval
        self._monitor_flag: bool = False
        self._task: asyncio.Task[None] | None = None

    async def _monitoring_loop(self) -> None:
        """Background loop that polls system stats periodically"""
        while self._monitor_flag:
            try:
                # Call the update callback to collect and update stats
                await self._update_callback()
                await asyncio.sleep(self._interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(self._interval)

    async def start_monitoring(self) -> None:
        """Start periodic system monitoring"""
        if self._monitor_flag:
            logger.debug("Monitoring already started")
            return

        logger.info(f"Starting system monitoring with {self._interval}s interval...")

        self._monitor_flag = True
        self._task = asyncio.create_task(self._monitoring_loop())

        logger.info("System monitoring started")

    async def stop_monitoring(self) -> None:
        """Stop periodic system monitoring"""
        if not self._monitor_flag:
            logger.debug("Monitoring already stopped")
            return

        logger.info("Stopping system monitoring...")

        self._monitor_flag = False
        if self._task:
            self._task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._task
            self._task = None

        logger.info("System monitoring stopped")
