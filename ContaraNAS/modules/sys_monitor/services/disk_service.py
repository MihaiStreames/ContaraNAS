from abc import ABC, abstractmethod
import platform

from ContaraNAS.core.utils import get_logger
from ContaraNAS.modules.sys_monitor.dtos import DiskInfo


logger = get_logger(__name__)


class DiskService(ABC):
    """Abstract base for Disk monitoring"""

    @abstractmethod
    def get_disk_info(self) -> list[DiskInfo]:
        """Get information for all disk partitions"""
        pass

    @staticmethod
    def create() -> "DiskService":
        """Factory method to create OS-specific service"""
        system = platform.system()

        if system == "Linux":
            from .linux.disk_service_linux import DiskServiceLinux  # noqa: PLC0415

            return DiskServiceLinux()
        if system == "Windows":
            # from .windows.disk_service_windows import DiskServiceWindows # noqa: PLC0415
            # return DiskServiceWindows()
            raise NotImplementedError("Windows not supported for Disk monitoring yet")
        raise NotImplementedError(f"OS '{system}' not supported for Disk monitoring")
