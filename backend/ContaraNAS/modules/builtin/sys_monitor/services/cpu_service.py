from abc import ABC, abstractmethod
import platform

from ContaraNAS.core.utils import get_logger
from ContaraNAS.modules.builtin.sys_monitor.dtos import CPUInfo


logger = get_logger(__name__)


class CPUService(ABC):
    """Abstract base for CPU monitoring"""

    @abstractmethod
    def get_cpu_info(self) -> CPUInfo:
        """Get comprehensive CPU information and usage stats"""
        ...

    def cleanup(self) -> None:  # noqa: B027
        """Clean up any resources - override if needed"""

    @staticmethod
    def create() -> "CPUService":
        """Factory method to create OS-specific service"""
        system = platform.system()

        if system == "Linux":
            from .linux.cpu_service_linux import CPUServiceLinux  # noqa: PLC0415

            return CPUServiceLinux()
        if system == "Windows":
            from .windows.cpu_service_windows import CPUServiceWindows  # noqa: PLC0415

            return CPUServiceWindows()
        raise NotImplementedError(f"OS '{system}' not supported for CPU monitoring")
