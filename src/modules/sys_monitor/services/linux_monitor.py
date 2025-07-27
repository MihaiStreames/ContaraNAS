from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class LinuxMonitor(ABC):
    """Base class for all monitoring services"""

    def __init__(self):
        self.proc_path = Path("/proc")
        self.sys_path = Path("/sys")

    @abstractmethod
    def get_info(self) -> Any:
        """Abstract method to get monitoring information"""
        pass
