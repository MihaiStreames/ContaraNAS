import re
from typing import Any, Dict, Optional


class FileParser:
    """Utility class for parsing system files"""

    @staticmethod
    def read_file_safe(file_path: str, encoding: str = "utf-8") -> Optional[str]:
        """Safely read a file, returning None if it fails"""
        try:
            with open(file_path, "r", encoding=encoding) as f:
                return f.read()
        except (IOError, OSError):
            return None

    @staticmethod
    def read_first_line(file_path: str) -> Optional[str]:
        """Read just the first line of a file"""
        try:
            with open(file_path, "r") as f:
                return f.readline().strip()
        except (IOError, OSError):
            return None


def parse_cpuinfo() -> Dict[str, Any]:
    """Parse /proc/cpuinfo"""
    cpuinfo = {}
    physical_ids = set()

    content = FileParser.read_file_safe("/proc/cpuinfo")
    if not content:
        return cpuinfo

    # Get model name
    model_match = re.search(r"model name\s*:\s*(.+)", content)
    if model_match:
        cpuinfo["model_name"] = model_match.group(1).strip()

    # Get CPU MHz
    mhz_match = re.search(r"cpu MHz\s*:\s*([0-9.]+)", content)
    if mhz_match:
        cpuinfo["cpu_mhz"] = float(mhz_match.group(1))

    # Get physical IDs
    for match in re.finditer(r"physical id\s*:\s*(\d+)", content):
        physical_ids.add(int(match.group(1)))

    cpuinfo["physical_ids"] = physical_ids
    return cpuinfo


def parse_meminfo() -> Dict[str, int]:
    """Parse /proc/meminfo"""
    meminfo = {}

    content = FileParser.read_file_safe("/proc/meminfo")
    if not content:
        return meminfo

    for line in content.split("\n"):
        if ":" in line:
            key, value = line.split(":", 1)
            # Extract numeric value (remove kB unit)
            value_match = re.search(r"(\d+)", value)
            if value_match:
                meminfo[key.strip()] = int(value_match.group(1))

    return meminfo


def parse_diskstats(device_name: str) -> Dict[str, Any]:
    """Parse /proc/diskstats for specific device"""
    content = FileParser.read_file_safe("/proc/diskstats")
    if not content:
        return {}

    for line in content.split("\n"):
        fields = line.split()
        if len(fields) >= 14 and fields[2] == device_name:
            # See Documentation/iostats.txt for field meanings
            reads = int(fields[5])  # sectors read
            writes = int(fields[9])  # sectors written
            read_time = int(fields[6])  # time spent reading (ms)
            write_time = int(fields[10])  # time spent writing (ms)
            io_time = int(fields[12])  # time spent doing I/Os (ms)

            return {
                "reads": reads,
                "writes": writes,
                "read_time": read_time,
                "write_time": write_time,
                "io_time": io_time,
            }

    return {}


def get_uptime() -> float:
    """Get system uptime in seconds"""
    uptime_str = FileParser.read_first_line("/proc/uptime")
    if uptime_str:
        return float(uptime_str.split()[0])
    return 0.0


def get_total_fd_count() -> int:
    """Get total file descriptor count"""
    content = FileParser.read_first_line("/proc/sys/fs/file-nr")
    if content:
        return int(content.split()[0])
    return 0
