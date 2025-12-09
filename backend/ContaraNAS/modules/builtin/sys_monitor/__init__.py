from dataclasses import asdict
from datetime import datetime

from ContaraNAS.core.action import Notify, OpenModal, action
from ContaraNAS.core.module import Module, ModuleState
from ContaraNAS.core.ui import Modal, Tile
from ContaraNAS.core.utils import get_logger

from .constants import DEFAULT_MONITOR_UPDATE_INTERVAL
from .services import (
    CPUService,
    DiskService,
    MemService,
    SysMonitorMonitoringService,
)
from .views import (
    build_cpu_modal,
    build_details_modal,
    build_disks_modal,
    build_memory_modal,
    build_tile,
)


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
            last_update=self.state.last_update,
            open_details_action=self.open_details,
        )

    def get_modals(self) -> list[Modal]:
        """Return modal definitions for this module"""
        return [
            build_details_modal(
                cpu=self.state.cpu,
                mem=self.state.memory,
                disks=self.state.disks,
                open_cpu_action=self.open_cpu_details,
                open_memory_action=self.open_memory_details,
                open_disk_action=self.open_disk_details,
            ),
            build_cpu_modal(self.state.cpu),
            build_memory_modal(self.state.memory),
            build_disks_modal(self.state.disks),
        ]

    # --- Actions ---

    @action
    async def refresh(self) -> Notify:
        """Manually refresh system stats"""
        await self._collect_stats()
        return Notify(message="System stats refreshed", variant="success")

    @action
    async def open_details(self) -> OpenModal:
        """Open the details modal"""
        # Refresh data before showing
        await self._collect_stats()
        return OpenModal(modal_id="sys_monitor_details")

    @action
    async def open_cpu_details(self) -> OpenModal:
        """Open the CPU details modal"""
        return OpenModal(modal_id="sys_monitor_cpu")

    @action
    async def open_memory_details(self) -> OpenModal:
        """Open the memory details modal"""
        return OpenModal(modal_id="sys_monitor_memory")

    @action
    async def open_disk_details(self) -> OpenModal:
        """Open the disk details modal"""
        return OpenModal(modal_id="sys_monitor_disks")
