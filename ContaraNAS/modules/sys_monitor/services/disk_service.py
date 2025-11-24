import json
from pathlib import Path
import platform
import re
import subprocess
from typing import Any

import psutil

from ContaraNAS.core.utils import get_logger
from ContaraNAS.modules.sys_monitor.constants import (
    DEFAULT_IO_UPDATE_INTERVAL,
    DISK_SECTOR_SIZE,
    IO_TIME_MS_DIVISOR,
)
from ContaraNAS.modules.sys_monitor.dtos import DiskInfo

from .hardware_cache_service import HardwareCacheService


logger = get_logger(__name__)


class DiskService:
    """Service to monitor disk information and usage"""

    def __init__(self, os_name: str | None = None):
        self._os_name: str = os_name or platform.system()
        self._hardware_cache = HardwareCacheService()
        self._previous_stats: dict[str, dict[str, Any]] = {}

        self._disk_types: dict[str, str] = {}
        self._disk_models: dict[str, str] = {}

        self._ensure_disk_cache_loaded()

    def _collect_disk_hardware_info(self) -> dict[str, Any]:
        """Collect disk hardware info"""
        partitions = psutil.disk_partitions()
        disk_models = {}
        disk_types = {}

        for partition in partitions:
            base_device = self._extract_base_device_name(partition.device)
            if base_device not in disk_models:
                disk_models[base_device] = self._get_device_model(partition.device)
                disk_types[base_device] = self._get_device_type(partition.device)

        return {
            "disk_models": disk_models,
            "disk_types": disk_types,
        }

    def _ensure_disk_cache_loaded(self):
        """Load disk hardware info from cache"""
        if not self._disk_models:
            hardware_info = self._hardware_cache.get_or_collect_hardware_info(
                self._collect_disk_hardware_info
            )
            self._disk_models = hardware_info.get("disk_models", {})
            self._disk_types = hardware_info.get("disk_types", {})

    @staticmethod
    def _extract_base_device_name(device: str) -> str:
        """Extract base device name from full device path

        Examples:
            /dev/sda1 -> sda
            /dev/nvme0n1p1 -> nvme0n1
            sdb2 -> sdb
        """
        base_device = device.split("/")[-1]
        if base_device.startswith("nvme"):
            # Handle NVMe devices: nvme0n1p1 -> nvme0n1
            # NVMe format: nvme<controller>n<namespace>p<partition>
            # Remove partition suffix (p<number>) if present
            match = re.match(r"(nvme\d+n\d+)", base_device)
            if match:
                base_device = match.group(1)
        else:
            # Handle regular devices: sda1 -> sda
            base_device = base_device.rstrip("0123456789")
        return base_device

    @staticmethod
    def _parse_diskstats(path: Path, device_name: str) -> dict[str, Any]:
        """Parse diskstats file for specific device"""
        diskstats = {}
        try:
            with Path.open(path, encoding="utf-8") as file:
                content = file.read()

            for line in content.splitlines():
                fields = line.split()
                if len(fields) >= 14 and fields[2] == device_name:
                    diskstats["reads"] = int(fields[5])
                    diskstats["writes"] = int(fields[9])
                    diskstats["read_time"] = int(fields[6])
                    diskstats["write_time"] = int(fields[10])
                    diskstats["io_time"] = int(fields[12])
                    break
        except (FileNotFoundError, PermissionError, OSError):
            pass

        return diskstats

    def _get_device_model(self, device: str) -> str:
        """Get the model name of the disk device using lsblk"""
        if self._os_name != "Linux":
            return "Unknown"

        base_device = self._extract_base_device_name(device)

        # Use lsblk with JSON output to get model name (works for all device types including NVMe)
        try:
            result = subprocess.run(
                ["lsblk", "-d", "-J", "-o", "NAME,MODEL"],
                capture_output=True,
                text=True,
                timeout=2,
                check=False,
            )

            if result.returncode == 0:
                data = json.loads(result.stdout)
                for block_device in data.get("blockdevices", []):
                    if block_device.get("name") == base_device:
                        model = str(block_device.get("model", "")).strip()
                        if model:
                            return model
        except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError, OSError):
            pass

        return "Unknown"

    def _get_device_type(self, device: str) -> str:
        """Determine if device is HDD, SSD, or NVMe"""
        if self._os_name != "Linux":
            return "Unknown"

        base_device = self._extract_base_device_name(device)

        # NVMe devices are a specific type
        if base_device.startswith("nvme"):
            return "NVMe"

        # Check if rotational (HDD vs SSD)
        rotational_path = Path(f"/sys/block/{base_device}/queue/rotational")
        if rotational_path.exists():
            try:
                is_rotational = rotational_path.read_text().strip()
                return "HDD" if is_rotational == "1" else "SSD"
            except Exception as e:
                logger.debug(f"Error reading rotational info for {base_device}: {e}")

        return "Unknown"

    def _get_disk_io_stats(self, device: str) -> dict[str, int]:
        """Get disk I/O statistics"""
        if self._os_name != "Linux":
            return {
                "read_bytes": 0,
                "write_bytes": 0,
                "read_time": 0,
                "write_time": 0,
                "io_time": 0,
            }

        base_device = self._extract_base_device_name(device)
        diskstats_path = Path("/proc/diskstats")
        stats = self._parse_diskstats(diskstats_path, base_device)

        read_bytes = stats.get("reads", 0) * DISK_SECTOR_SIZE
        write_bytes = stats.get("writes", 0) * DISK_SECTOR_SIZE

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
        partitions = psutil.disk_partitions()

        logger.debug(f"Found {len(partitions)} disk partitions")

        for partition in partitions:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                io_stats = self._get_disk_io_stats(partition.device)

                # Calculate speeds based on previous stats
                read_speed = 0.0
                write_speed = 0.0
                busy_time = 0.0

                device_key = partition.device
                if device_key in self._previous_stats:
                    prev = self._previous_stats[device_key]
                    read_diff = io_stats["read_bytes"] - prev["read_bytes"]
                    write_diff = io_stats["write_bytes"] - prev["write_bytes"]
                    io_time_diff = io_stats["io_time"] - prev["io_time"]

                    # Calculate speeds based on default update interval
                    read_speed = read_diff / DEFAULT_IO_UPDATE_INTERVAL if read_diff > 0 else 0.0
                    write_speed = write_diff / DEFAULT_IO_UPDATE_INTERVAL if write_diff > 0 else 0.0
                    busy_time = (
                        (io_time_diff / IO_TIME_MS_DIVISOR) / DEFAULT_IO_UPDATE_INTERVAL
                        if io_time_diff > 0
                        else 0.0
                    )

                # Store current stats for next calculation
                self._previous_stats[device_key] = io_stats.copy()

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
                    model=self._get_device_model(partition.device),
                    type=self._get_device_type(partition.device),
                )
                disks.append(disk_info)
                logger.debug(f"Added disk: {partition.mountpoint} ({partition.device})")

            except (PermissionError, OSError) as e:
                # Skip partitions that can't be accessed
                logger.debug(f"Skipping partition {partition.mountpoint}: {e}")
                continue

        logger.debug(f"Returning {len(disks)} disk(s)")
        return disks
