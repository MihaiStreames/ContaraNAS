from abc import ABC, abstractmethod
import platform

from ContaraNAS.core.utils import get_logger
from ContaraNAS.modules.builtin.sys_monitor.dtos import MemoryInfo


logger = get_logger(__name__)


class MemService(ABC):
    """Abstract base for Memory monitoring"""

    @abstractmethod
    def get_memory_info(self) -> MemoryInfo:
        """Get comprehensive Memory information and usage stats"""
        ...

    def cleanup(self) -> None:  # noqa: B027
        """Clean up any resources - override if needed"""

    @staticmethod
    def create() -> "MemService":
        """Factory method to create OS-specific service"""
        system = platform.system()

        if system == "Linux":
            from .linux.mem_service_linux import MemServiceLinux  # noqa: PLC0415

            return MemServiceLinux()
        if system == "Windows":
            from .windows.mem_service_windows import MemServiceWindows  # noqa: PLC0415

            return MemServiceWindows()
        raise NotImplementedError(f"OS '{system}' not supported for Memory monitoring")
