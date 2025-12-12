from fastapi import APIRouter, Depends, HTTPException, Request, status

from ContaraNAS.api.responses import ModuleInfo, ModuleListResponse, ModuleToggleResponse
from ContaraNAS.core.module_manager import ModuleManager
from ContaraNAS.core import get_logger

from .auth import require_auth


logger = get_logger(__name__)


def _get_manager(request: Request) -> ModuleManager:
    """Extract module manager from app state"""
    return request.app.state.module_manager


def _require_module(request: Request, name: str) -> None:
    """Raise 404 if module doesn't exist"""
    manager = _get_manager(request)

    if name not in manager.modules:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Module '{name}' not found")


def create_command_routes() -> APIRouter:
    """Create API router with module control endpoints"""
    router = APIRouter(prefix="/api", tags=["commands"])

    @router.get("/modules", response_model=ModuleListResponse)
    async def list_modules(
        request: Request,
        _: None = Depends(require_auth),
    ) -> ModuleListResponse:
        """List all registered modules with their current state"""
        manager = _get_manager(request)

        modules = []
        for name, module in manager.modules.items():
            metadata = module.metadata
            source = metadata.source if metadata else "builtin"
            version = metadata.version if metadata else "0.0.0"
            system_deps = metadata.dependencies.system if metadata else []

            modules.append(
                ModuleInfo(
                    name=name,
                    display_name=module.display_name,
                    enabled=module.enable_flag,
                    initialized=module.init_flag,
                    source=source,
                    removable=source == "community",
                    version=version,
                    system_deps=system_deps,
                )
            )

        return ModuleListResponse(modules=modules)

    @router.post("/modules/{name}/enable", response_model=ModuleToggleResponse)
    async def enable_module(
        name: str,
        request: Request,
        _: None = Depends(require_auth),
    ) -> ModuleToggleResponse:
        """Enable a registered module"""
        _require_module(request, name)
        manager = _get_manager(request)

        try:
            await manager.enable_module(name)
            return ModuleToggleResponse(success=True, module=name, enabled=True)

        except Exception as e:
            logger.error(f"Failed to enable {name}: {e}")
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e)) from e

    @router.post("/modules/{name}/disable", response_model=ModuleToggleResponse)
    async def disable_module(
        name: str,
        request: Request,
        _: None = Depends(require_auth),
    ) -> ModuleToggleResponse:
        """Disable an enabled module"""
        _require_module(request, name)
        manager = _get_manager(request)

        try:
            await manager.disable_module(name)
            return ModuleToggleResponse(success=True, module=name, enabled=False)

        except Exception as e:
            logger.error(f"Failed to disable {name}: {e}")
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e)) from e

    return router
