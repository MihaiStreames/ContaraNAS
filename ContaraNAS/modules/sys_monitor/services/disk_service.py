import platform
from pathlib import Path

import psutil

from ContaraNAS.modules.sys_monitor.dtos import DiskInfo
from ContaraNAS.modules.sys_monitor.linux.parse_diskstats import parse_diskstats


class DiskService:
    """Service to monitor disk information and usage"""

    def __init__(self, os_name=None):
        self.os_name = os_name or platform.system()
        self.previous_stats = {}

    def __get_device_model(self, device: str) -> str:
        """Get the model name of the disk device"""
        if self.os_name != "Linux":
            return "Unknown"

        # Extract base device name (e.g., sda from sda1, nvme0n1 from nvme0n1p1)
        base_device = device.split("/")[-1]
        if base_device.startswith("nvme"):
            base_device = base_device.rstrip("0123456789p")
            if base_device.endswith("p"):
                base_device = base_device[:-1]
        else:
            base_device = base_device.rstrip("0123456789")

        model_path = Path(f"/sys/block/{base_device}/device/model")
        if model_path.exists():
            try:
                return model_path.read_text().strip()
            except Exception:
                pass
        return "Unknown"

    def __get_device_type(self, device: str) -> str:
        """Determine if device is HDD or SSD"""
        if self.os_name != "Linux":
            return "Unknown"

        # Extract base device name
        base_device = device.split("/")[-1]
        if base_device.startswith("nvme"):
            return "SSD"

        base_device = base_device.rstrip("0123456789")
        rotational_path = Path(f"/sys/block/{base_device}/queue/rotational")
        if rotational_path.exists():
            try:
                is_rotational = rotational_path.read_text().strip()
                return "HDD" if is_rotational == "1" else "SSD"
            except Exception:
                pass
        return "Unknown"

    def __get_disk_io_stats(self, device: str) -> dict:
        """Get disk I/O statistics"""
        if self.os_name != "Linux":
            return {
                "read_bytes": 0,
                "write_bytes": 0,
                "read_time": 0,
                "write_time": 0,
                "io_time": 0,
            }

        # Extract base device name for diskstats lookup
        base_device = device.split("/")[-1]
        if base_device.startswith("nvme"):
            base_device = base_device.rstrip("0123456789p")
            if base_device.endswith("p"):
                base_device = base_device[:-1]
        else:
            base_device = base_device.rstrip("0123456789")

        diskstats_path = Path("/proc/diskstats")
        stats = parse_diskstats(diskstats_path, base_device)

        # Sector size is typically 512 bytes
        sector_size = 512
        read_bytes = stats.get("reads", 0) * sector_size
        write_bytes = stats.get("writes", 0) * sector_size

        return {
            "read_bytes": read_bytes,
            "write_bytes": write_bytes,
            "read_time": stats.get("read_time", 0),
            "write_time": stats.get("write_time", 0),
            "io_time": stats.get("io_time", 0),
        }

    def get_disk_info(self) -> list[DiskInfo]:
        """Get information for all disk partitions"""
        disks = []

        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                io_stats = self.__get_disk_io_stats(partition.device)

                # Calculate speeds based on previous stats
                read_speed = 0.0
                write_speed = 0.0
                busy_time = 0.0

                device_key = partition.device
                if device_key in self.previous_stats:
                    prev = self.previous_stats[device_key]
                    read_diff = io_stats["read_bytes"] - prev["read_bytes"]
                    write_diff = io_stats["write_bytes"] - prev["write_bytes"]
                    io_time_diff = io_stats["io_time"] - prev["io_time"]

                    # Assuming update interval of ~2 seconds (will be adjusted by monitoring service)
                    time_interval = 2.0
                    read_speed = read_diff / time_interval if read_diff > 0 else 0.0
                    write_speed = write_diff / time_interval if write_diff > 0 else 0.0
                    busy_time = (io_time_diff / 10.0) / time_interval if io_time_diff > 0 else 0.0

                # Store current stats for next calculation
                self.previous_stats[device_key] = io_stats.copy()

                disk_info = DiskInfo(
                    device=partition.device,
                    mountpoint=partition.mountpoint,
                    filesystem=partition.fstype,
                    total_gb=usage.total / (1024**3),
                    used_gb=usage.used / (1024**3),
                    free_gb=usage.free / (1024**3),
                    usage_percent=usage.percent,
                    read_bytes=io_stats["read_bytes"],
                    write_bytes=io_stats["write_bytes"],
                    read_speed=read_speed,
                    write_speed=write_speed,
                    read_time=io_stats["read_time"],
                    write_time=io_stats["write_time"],
                    io_time=io_stats["io_time"],
                    busy_time=busy_time,
                    model=self.__get_device_model(partition.device),
                    type=self.__get_device_type(partition.device),
                )
                disks.append(disk_info)

            except (PermissionError, OSError) as e:
                # Skip partitions that can't be accessed
                continue

        return disks
