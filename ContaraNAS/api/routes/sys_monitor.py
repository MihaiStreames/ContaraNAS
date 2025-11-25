from dataclasses import asdict
from typing import TYPE_CHECKING

from fastapi import APIRouter, HTTPException, status

from ContaraNAS.api.schemas import (
    CPUInfoResponse,
    DiskInfoResponse,
    MemoryInfoResponse,
    RAMStickResponse,
    SystemStatsResponse,
)
from ContaraNAS.core.utils import get_logger

if TYPE_CHECKING:
    from ContaraNAS.core.module_manager import ModuleManager

logger = get_logger(__name__)


def create_system_router(module_manager: "ModuleManager") -> APIRouter:
    """Create the system monitor router with the module manager dependency"""

    router = APIRouter(prefix="/system", tags=["system"])

    def _get_sys_monitor_controller():
        """Helper to get the sys_monitor controller, raising if unavailable"""
        module = module_manager.modules.get("sys_monitor")

        if not module:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="System monitor module not found",
            )

        if not module.enable_flag:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="System monitor module is not enabled",
            )

        if not module.controller:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="System monitor controller not initialized",
            )

        return module.controller

    @router.get("/stats", response_model=SystemStatsResponse)
    async def get_system_stats() -> SystemStatsResponse:
        """Get complete system statistics (CPU, Memory, Disks)"""
        controller = _get_sys_monitor_controller()

        try:
            tile_data = await controller.get_tile_data()

            # Convert CPU info
            cpu_data = tile_data.get("cpu")
            cpu_response = None
            if cpu_data:
                cpu_dict = asdict(cpu_data) if hasattr(cpu_data, "__dataclass_fields__") else cpu_data
                cpu_response = CPUInfoResponse(**cpu_dict)

            # Convert Memory info
            mem_data = tile_data.get("memory")
            mem_response = None
            if mem_data:
                mem_dict = asdict(mem_data) if hasattr(mem_data, "__dataclass_fields__") else mem_data
                # Handle RAM sticks
                if "ram_sticks" in mem_dict and mem_dict["ram_sticks"]:
                    mem_dict["ram_sticks"] = [
                        RAMStickResponse(**asdict(stick) if hasattr(stick, "__dataclass_fields__") else stick)
                        for stick in mem_dict["ram_sticks"]
                    ]
                mem_response = MemoryInfoResponse(**mem_dict)

            # Convert Disk info
            disks_data = tile_data.get("disks", [])
            disks_response = []
            for disk in disks_data:
                disk_dict = asdict(disk) if hasattr(disk, "__dataclass_fields__") else disk
                disks_response.append(DiskInfoResponse(**disk_dict))

            return SystemStatsResponse(
                cpu=cpu_response,
                memory=mem_response,
                disks=disks_response,
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting system stats: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error getting system stats: {e!s}",
            ) from e

    @router.get("/cpu", response_model=CPUInfoResponse)
    async def get_cpu_info() -> CPUInfoResponse:
        """Get CPU information and usage"""
        controller = _get_sys_monitor_controller()

        try:
            cpu_info = controller.cpu_service.get_cpu_info()
            cpu_dict = asdict(cpu_info)
            return CPUInfoResponse(**cpu_dict)

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting CPU info: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error getting CPU info: {e!s}",
            ) from e

    @router.get("/memory", response_model=MemoryInfoResponse)
    async def get_memory_info() -> MemoryInfoResponse:
        """Get memory information and usage"""
        controller = _get_sys_monitor_controller()

        try:
            mem_info = controller.mem_service.get_memory_info()
            mem_dict = asdict(mem_info)

            # Handle RAM sticks
            if "ram_sticks" in mem_dict and mem_dict["ram_sticks"]:
                mem_dict["ram_sticks"] = [
                    RAMStickResponse(**stick) for stick in mem_dict["ram_sticks"]
                ]

            return MemoryInfoResponse(**mem_dict)

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting memory info: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error getting memory info: {e!s}",
            ) from e

    @router.get("/disks", response_model=list[DiskInfoResponse])
    async def get_disks_info() -> list[DiskInfoResponse]:
        """Get information about all disk partitions"""
        controller = _get_sys_monitor_controller()

        try:
            disks = controller.disk_service.get_disk_info()
            return [DiskInfoResponse(**asdict(disk)) for disk in disks]

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting disk info: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error getting disk info: {e!s}",
            ) from e

    @router.get("/disks/{mountpoint:path}", response_model=DiskInfoResponse)
    async def get_disk_by_mountpoint(mountpoint: str) -> DiskInfoResponse:
        """Get information about a specific disk by mountpoint"""
        controller = _get_sys_monitor_controller()

        # Ensure mountpoint starts with /
        if not mountpoint.startswith("/"):
            mountpoint = "/" + mountpoint

        try:
            disks = controller.disk_service.get_disk_info()
            for disk in disks:
                if disk.mountpoint == mountpoint:
                    return DiskInfoResponse(**asdict(disk))

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Disk with mountpoint '{mountpoint}' not found",
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting disk info: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error getting disk info: {e!s}",
            ) from e

    @router.get("/uptime")
    async def get_uptime() -> dict:
        """Get system uptime"""
        controller = _get_sys_monitor_controller()

        try:
            cpu_info = controller.cpu_service.get_cpu_info()
            uptime_seconds = cpu_info.uptime

            # Calculate human-readable uptime
            days = int(uptime_seconds // 86400)
            hours = int((uptime_seconds % 86400) // 3600)
            minutes = int((uptime_seconds % 3600) // 60)
            seconds = int(uptime_seconds % 60)

            return {
                "uptime_seconds": uptime_seconds,
                "uptime_formatted": f"{days}d {hours}h {minutes}m {seconds}s",
                "days": days,
                "hours": hours,
                "minutes": minutes,
                "seconds": seconds,
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting uptime: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error getting uptime: {e!s}",
            ) from e

    @router.get("/summary")
    async def get_system_summary() -> dict:
        """Get a quick summary of system status"""
        controller = _get_sys_monitor_controller()

        try:
            cpu_info = controller.cpu_service.get_cpu_info()
            mem_info = controller.mem_service.get_memory_info()
            disks = controller.disk_service.get_disk_info()

            return {
                "cpu": {
                    "name": cpu_info.name,
                    "cores": cpu_info.logical_cores,
                    "usage_percent": cpu_info.total_usage,
                    "speed_ghz": cpu_info.current_speed_ghz,
                },
                "memory": {
                    "total_gb": mem_info.total / (1024 ** 3),
                    "used_gb": mem_info.used / (1024 ** 3),
                    "usage_percent": mem_info.usage,
                },
                "disks": [
                    {
                        "mountpoint": disk.mountpoint,
                        "total_gb": disk.total_gb,
                        "used_gb": disk.used_gb,
                        "usage_percent": disk.usage_percent,
                    }
                    for disk in disks
                ],
                "process_count": cpu_info.processes,
                "thread_count": cpu_info.threads,
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting system summary: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error getting system summary: {e!s}",
            ) from e

    return router
