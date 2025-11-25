from typing import TYPE_CHECKING, Any

from fastapi import APIRouter, HTTPException, status

from ContaraNAS.api.schemas import (
    ModuleInfoResponse,
    ModuleListResponse,
    ModuleToggleRequest,
    ModuleToggleResponse,
)
from ContaraNAS.core.utils import get_logger

if TYPE_CHECKING:
    from ContaraNAS.core.module_manager import ModuleManager

logger = get_logger(__name__)


def create_modules_router(module_manager: "ModuleManager") -> APIRouter:
    """Create the modules router with the module manager dependency"""

    router = APIRouter(prefix="/modules", tags=["modules"])

    @router.get("", response_model=ModuleListResponse)
    async def list_modules() -> ModuleListResponse:
        """Get list of all available modules and their states"""
        modules: list[ModuleInfoResponse] = []
        enabled_count = 0

        for name, module in module_manager.modules.items():
            tile_data = await module.get_tile_data()

            modules.append(
                ModuleInfoResponse(
                    name=name,
                    display_name=module.display_name,
                    enabled=module.enable_flag,
                    initialized=module.init_flag,
                    state=module.state.copy(),
                    tile_data=tile_data,
                )
            )

            if module.enable_flag:
                enabled_count += 1

        return ModuleListResponse(
            modules=modules,
            total_count=len(modules),
            enabled_count=enabled_count,
        )

    @router.get("/{module_name}", response_model=ModuleInfoResponse)
    async def get_module(module_name: str) -> ModuleInfoResponse:
        """Get detailed information about a specific module"""
        if module_name not in module_manager.modules:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Module '{module_name}' not found",
            )

        module = module_manager.modules[module_name]
        tile_data = await module.get_tile_data()

        return ModuleInfoResponse(
            name=module_name,
            display_name=module.display_name,
            enabled=module.enable_flag,
            initialized=module.init_flag,
            state=module.state.copy(),
            tile_data=tile_data,
        )

    @router.post("/{module_name}/toggle", response_model=ModuleToggleResponse)
    async def toggle_module(
            module_name: str, request: ModuleToggleRequest
    ) -> ModuleToggleResponse:
        """Enable or disable a module"""
        if module_name not in module_manager.modules:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Module '{module_name}' not found",
            )

        try:
            if request.enabled:
                await module_manager.enable_module(module_name)
                message = f"Module '{module_name}' enabled successfully"
            else:
                await module_manager.disable_module(module_name)
                message = f"Module '{module_name}' disabled successfully"

            return ModuleToggleResponse(
                success=True,
                message=message,
                module_name=module_name,
                enabled=request.enabled,
            )

        except Exception as e:
            logger.error(f"Failed to toggle module '{module_name}': {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to toggle module: {e!s}",
            ) from e

    @router.post("/{module_name}/enable", response_model=ModuleToggleResponse)
    async def enable_module(module_name: str) -> ModuleToggleResponse:
        """Enable a specific module"""
        if module_name not in module_manager.modules:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Module '{module_name}' not found",
            )

        module = module_manager.modules[module_name]
        if module.enable_flag:
            return ModuleToggleResponse(
                success=True,
                message=f"Module '{module_name}' is already enabled",
                module_name=module_name,
                enabled=True,
            )

        try:
            await module_manager.enable_module(module_name)
            return ModuleToggleResponse(
                success=True,
                message=f"Module '{module_name}' enabled successfully",
                module_name=module_name,
                enabled=True,
            )
        except Exception as e:
            logger.error(f"Failed to enable module '{module_name}': {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to enable module: {e!s}",
            ) from e

    @router.post("/{module_name}/disable", response_model=ModuleToggleResponse)
    async def disable_module(module_name: str) -> ModuleToggleResponse:
        """Disable a specific module"""
        if module_name not in module_manager.modules:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Module '{module_name}' not found",
            )

        module = module_manager.modules[module_name]
        if not module.enable_flag:
            return ModuleToggleResponse(
                success=True,
                message=f"Module '{module_name}' is already disabled",
                module_name=module_name,
                enabled=False,
            )

        try:
            await module_manager.disable_module(module_name)
            return ModuleToggleResponse(
                success=True,
                message=f"Module '{module_name}' disabled successfully",
                module_name=module_name,
                enabled=False,
            )
        except Exception as e:
            logger.error(f"Failed to disable module '{module_name}': {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to disable module: {e!s}",
            ) from e

    @router.get("/{module_name}/state", response_model=dict[str, Any])
    async def get_module_state(module_name: str) -> dict[str, Any]:
        """Get the current state of a module"""
        state = await module_manager.get_module_state(module_name)

        if state is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Module '{module_name}' not found",
            )

        return state

    @router.get("/{module_name}/tile", response_model=dict[str, Any])
    async def get_module_tile_data(module_name: str) -> dict[str, Any]:
        """Get tile data for a module (for dashboard display)"""
        if module_name not in module_manager.modules:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Module '{module_name}' not found",
            )

        module = module_manager.modules[module_name]
        return await module.get_tile_data()

    return router
