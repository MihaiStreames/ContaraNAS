import json
from pathlib import Path
import re
import subprocess
from typing import Any

import psutil

from ContaraNAS.core.utils import get_logger
from ContaraNAS.modules.builtin.sys_monitor.constants import (
    DEFAULT_IO_UPDATE_INTERVAL,
    DISK_SECTOR_SIZE,
    IO_TIME_MS_DIVISOR,
)
from ContaraNAS.modules.builtin.sys_monitor.dtos import DiskInfo
from ContaraNAS.modules.builtin.sys_monitor.services import (
    DiskService,
    HardwareCacheService,
)


logger = get_logger(__name__)


class DiskServiceLinux(DiskService):
    """Linux-specific Disk monitoring implementation"""

    def __init__(self):
        self._hardware_cache = HardwareCacheService(cache_name="disk")
        self._previous_stats: dict[str, dict[str, Any]] = {}

        # In-memory cache of disk hardware attributes
        self._disk_types: dict[str, str] = {}
        self._disk_models: dict[str, str] = {}

        self._load_existing_disk_cache()

    @staticmethod
    def _extract_base_device_name(device: str) -> str:
        """Extract base device name from full device path"""
        base_device = device.split("/")[-1]
        if base_device.startswith("nvme"):
            match = re.match(r"(nvme\d+n\d+)", base_device)
            if match:
                base_device = match.group(1)
        else:
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
        base_device = self._extract_base_device_name(device)

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

    def _collect_disk_hardware_info(self, device: str) -> tuple[str, str]:
        """Get model and type for a disk, using cache or collecting fresh data"""
        base_device = self._extract_base_device_name(device)

        # Check if we already have this disk's info in memory
        if base_device in self._disk_models and base_device in self._disk_types:
            return self._disk_models[base_device], self._disk_types[base_device]

        # New disk discovered - collect its hardware info
        logger.debug(f"Discovering hardware info for new disk: {base_device}")
        model = self._get_device_model(device)
        disk_type = self._get_device_type(device)

        # Cache in memory
        self._disk_models[base_device] = model
        self._disk_types[base_device] = disk_type

        # Persist to disk cache
        self._save_disk_cache()

        return model, disk_type

    def _save_disk_cache(self):
        """Save current disk hardware info to cache"""
        hardware_data = {
            "disk_models": self._disk_models,
            "disk_types": self._disk_types,
        }
        self._hardware_cache.save_cache(hardware_data)
        logger.debug(f"Saved disk cache with {len(self._disk_models)} disks")

    def _load_existing_disk_cache(self):
        """Load previously cached disk hardware info"""
        cached_data = self._hardware_cache.load_cache()
        if cached_data:
            self._disk_models = cached_data.get("disk_models", {})
            self._disk_types = cached_data.get("disk_types", {})
            logger.debug(f"Loaded cached info for {len(self._disk_models)} disks")

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

                # Get hardware info (uses cache for known disks, discovers new ones)
                model, disk_type = self._collect_disk_hardware_info(partition.device)

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
                    model=model,
                    type=disk_type,
                )
                disks.append(disk_info)
                logger.debug(f"Added disk: {partition.mountpoint} ({partition.device})")

            except (PermissionError, OSError) as e:
                logger.debug(f"Skipping partition {partition.mountpoint}: {e}")
                continue

        logger.debug(f"Returning {len(disks)} disk(s)")
        return disks
