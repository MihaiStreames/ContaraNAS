from dataclasses import asdict
from datetime import datetime

from ContaraNAS.core.action import Notify, action
from ContaraNAS.core.module import Module, ModuleState
from ContaraNAS.core.ui import Tile
from ContaraNAS.core.utils import get_logger

from .constants import DEFAULT_MONITOR_UPDATE_INTERVAL, HISTORY_SIZE
from .services import (
    CPUService,
    DiskService,
    MemService,
    SysMonitorMonitoringService,
)
from .views import build_tile


logger = get_logger(__name__)


class SysMonitorModule(Module):
    """Module for monitoring your NAS system"""

    class State(ModuleState):
        """System monitor state"""

        initialized_at: datetime | None = None
        last_update: datetime | None = None
        cpu: dict | None = None
        memory: dict | None = None
        disks: list[dict] = []
        error: str | None = None
        # History buffers for graphs
        cpu_history: list[float] = []
        memory_history: list[float] = []
        disk_history: dict[str, list[float]] = {}  # device -> busy_time history

    def __init__(
        self,
        name: str = "sys_monitor",
        display_name: str | None = None,
        metadata=None,
    ) -> None:
        super().__init__(name, display_name or "System Monitor", metadata)

        # Initialize services (platform-specific)
        self._cpu_service = CPUService.create()
        self._mem_service = MemService.create()
        self._disk_service = DiskService.create()
        self._monitoring_service: SysMonitorMonitoringService | None = None
        self._update_interval = DEFAULT_MONITOR_UPDATE_INTERVAL

    @property
    def state(self) -> "SysMonitorModule.State":
        """Type-safe state accessor"""
        assert self._typed_state is not None
        return self._typed_state

    async def initialize(self) -> None:
        """Initialize the SysMonitor module"""
        logger.info("Initializing System Monitor module...")

        # Set up monitoring service with our collection method
        self._monitoring_service = SysMonitorMonitoringService(
            self._collect_stats, interval=self._update_interval
        )

        self.state.initialized_at = datetime.now()
        self.state.commit()

        logger.info("System Monitor module initialized successfully")

    async def start_monitoring(self) -> None:
        """Start System monitoring"""
        if self._monitoring_service:
            await self._monitoring_service.start_monitoring()
            logger.info("System monitoring started")

    async def stop_monitoring(self) -> None:
        """Stop System monitoring"""
        if self._monitoring_service:
            await self._monitoring_service.stop_monitoring()

        # Clean up OS-specific resources
        self._cpu_service.cleanup()
        self._mem_service.cleanup()
        self._disk_service.cleanup()

        logger.info("System monitoring stopped")

    async def _collect_stats(self) -> None:
        """Collect all system stats and update state"""
        try:
            cpu_info = self._cpu_service.get_cpu_info()
            mem_info = self._mem_service.get_memory_info()
            disk_info = self._disk_service.get_disk_info()

            # Convert dataclasses to dicts for state storage
            self.state.cpu = asdict(cpu_info) if cpu_info else None
            self.state.memory = asdict(mem_info) if mem_info else None
            self.state.disks = [asdict(d) for d in disk_info] if disk_info else []
            self.state.last_update = datetime.now()
            self.state.error = None

            # Update history buffers
            if cpu_info:
                self.state.cpu_history.append(cpu_info.total_usage)
                if len(self.state.cpu_history) > HISTORY_SIZE:
                    self.state.cpu_history = self.state.cpu_history[-HISTORY_SIZE:]

            if mem_info:
                self.state.memory_history.append(mem_info.usage)
                if len(self.state.memory_history) > HISTORY_SIZE:
                    self.state.memory_history = self.state.memory_history[-HISTORY_SIZE:]

            # Update disk history (keyed by device)
            if disk_info:
                for disk in disk_info:
                    device = disk.device
                    if device not in self.state.disk_history:
                        self.state.disk_history[device] = []
                    self.state.disk_history[device].append(disk.busy_time)
                    if len(self.state.disk_history[device]) > HISTORY_SIZE:
                        self.state.disk_history[device] = self.state.disk_history[device][
                            -HISTORY_SIZE:
                        ]

            self.state.commit()

        except Exception as e:
            logger.error(f"Error collecting system stats: {e}")
            self.state.error = str(e)
            self.state.commit()

    def get_tile(self) -> Tile:
        """Return the dashboard tile UI component"""
        return build_tile(
            cpu=self.state.cpu,
            mem=self.state.memory,
            disks=self.state.disks,
            cpu_history=self.state.cpu_history,
            memory_history=self.state.memory_history,
            disk_history=self.state.disk_history,
            last_update=self.state.last_update,
        )

    # --- Actions ---

    @action
    async def refresh(self) -> Notify:
        """Manually refresh system stats"""
        await self._collect_stats()
        return Notify(message="System stats refreshed", variant="success")
