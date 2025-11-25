import json
import subprocess
from typing import Any

import psutil
import wmi

from backend.ContaraNAS.core.utils import get_logger
from backend.ContaraNAS.modules.sys_monitor.constants import DEFAULT_IO_UPDATE_INTERVAL
from backend.ContaraNAS.modules.sys_monitor.dtos import DiskInfo
from backend.ContaraNAS.modules.sys_monitor.services import DiskService, HardwareCacheService


logger = get_logger(__name__)


class DiskServiceWindows(DiskService):
    """Windows-specific Disk monitoring implementation"""

    def __init__(self):
        self._hardware_cache = HardwareCacheService(cache_name="disk")
        self._previous_stats: dict[str, dict[str, Any]] = {}

        # In-memory cache of disk hardware attributes
        self._disk_types: dict[str, str] = {}
        self._disk_models: dict[str, str] = {}

        self._load_existing_disk_cache()

    @staticmethod
    def _get_disk_hardware_info_wmi() -> dict[str, dict[str, str]]:
        """Get disk hardware info using WMI and PowerShell"""

        c = wmi.WMI()
        disk_info = {}

        # Get physical disks via WMI
        for disk in c.Win32_DiskDrive():
            device_id = disk.DeviceID  # e.g., \\.\PHYSICALDRIVE0
            model = (disk.Model or "Unknown").strip()

            # Default to Unknown
            disk_type = "Unknown"

            # Try to get MediaType from Get-PhysicalDisk
            try:
                # Get the disk number from DeviceID
                disk_num = device_id.split("PHYSICALDRIVE")[-1]

                # Use PowerShell to get BusType and MediaType
                ps_command = f"Get-PhysicalDisk -DeviceNumber {disk_num} | Select-Object BusType, MediaType | ConvertTo-Json"
                result = subprocess.run(
                    ["powershell", "-Command", ps_command],
                    check=False,
                    capture_output=True,
                    text=True,
                    timeout=5,
                )

                if result.returncode == 0:
                    data = json.loads(result.stdout)
                    bus_type = data.get("BusType", "")
                    media_type = data.get("MediaType", "")

                    # Determine type based on BusType and MediaType
                    if "NVMe" in str(bus_type) or bus_type == 17:  # 17 = NVMe
                        disk_type = "NVMe"
                    elif media_type == 4 or "SSD" in str(media_type):  # 4 = SSD
                        disk_type = "SSD"
                    elif media_type == 3 or "HDD" in str(media_type):  # 3 = HDD
                        disk_type = "HDD"
                    else:
                        disk_type = "SSD"  # Default assumption for modern systems

            except Exception as e:
                logger.debug(f"Error getting disk type via PowerShell: {e}")

            disk_info[device_id] = {"model": model, "type": disk_type}

        return disk_info

    def _get_disk_hardware_info(self, device: str) -> tuple[str, str]:
        """Get model and type for a disk, using cache or collecting fresh data"""
        # For partitions like C:, we need to map to physical disk
        # In reality we'd need to map partition to physical disk

        if device in self._disk_models and device in self._disk_types:
            return self._disk_models[device], self._disk_types[device]

        # Check if we have cached data for all disks
        if not self._disk_models:
            # Collect all disk info at once
            all_disk_info = self._get_disk_hardware_info_wmi()

            for dev_id, info in all_disk_info.items():
                self._disk_models[dev_id] = info["model"]
                self._disk_types[dev_id] = info["type"]

            self._save_disk_cache()

        # Try to find matching disk for this partition
        # Simplified: use first disk info as fallback
        if self._disk_models:
            first_key = list(self._disk_models.keys())[0]
            return self._disk_models.get(
                device, self._disk_models[first_key]
            ), self._disk_types.get(device, self._disk_types[first_key])

        return "Unknown", "Unknown"

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
                io_counters = psutil.disk_io_counters(perdisk=False)

                # Calculate speeds based on previous stats
                read_speed = 0.0
                write_speed = 0.0
                busy_time = 0.0

                read_bytes = io_counters.read_bytes if io_counters else 0
                write_bytes = io_counters.write_bytes if io_counters else 0
                read_time = io_counters.read_time if io_counters else 0
                write_time = io_counters.write_time if io_counters else 0

                device_key = partition.device
                if device_key in self._previous_stats and io_counters:
                    prev = self._previous_stats[device_key]
                    read_diff = read_bytes - prev["read_bytes"]
                    write_diff = write_bytes - prev["write_bytes"]

                    read_speed = read_diff / DEFAULT_IO_UPDATE_INTERVAL if read_diff > 0 else 0.0
                    write_speed = write_diff / DEFAULT_IO_UPDATE_INTERVAL if write_diff > 0 else 0.0

                # Store current stats for next calculation
                self._previous_stats[device_key] = {
                    "read_bytes": read_bytes,
                    "write_bytes": write_bytes,
                    "read_time": read_time,
                    "write_time": write_time,
                }

                # Get hardware info
                model, disk_type = self._get_disk_hardware_info(partition.device)

                disk_info = DiskInfo(
                    device=partition.device,
                    mountpoint=partition.mountpoint,
                    filesystem=partition.fstype,
                    total_gb=usage.total / (1024**3),
                    used_gb=usage.used / (1024**3),
                    free_gb=usage.free / (1024**3),
                    usage_percent=usage.percent,
                    read_bytes=read_bytes,
                    write_bytes=write_bytes,
                    read_speed=read_speed,
                    write_speed=write_speed,
                    read_time=read_time,
                    write_time=write_time,
                    io_time=0,  # Not readily available on Windows
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
