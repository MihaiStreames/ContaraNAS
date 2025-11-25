from backend.ContaraNAS.core.utils import get_logger
from fastapi import APIRouter, HTTPException, Request, status


logger = get_logger(__name__)


def create_command_routes() -> APIRouter:
    """Create API router with module control endpoints"""
    router = APIRouter(prefix="/api", tags=["commands"])

    def get_manager(request: Request):
        """Extract module manager from app state"""
        return request.app.state.module_manager

    @router.get("/modules")
    async def list_modules(request: Request) -> dict:
        """List all registered modules with their current state"""
        manager = get_manager(request)

        modules = []
        for name, module in manager.modules.items():
            modules.append(
                {
                    "name": name,
                    "display_name": module.display_name,
                    "enabled": module.enable_flag,
                    "initialized": module.init_flag,
                }
            )

        return {"modules": modules}

    @router.post("/modules/{name}/enable")
    async def enable_module(name: str, request: Request) -> dict:
        """Enable a registered module"""
        manager = get_manager(request)

        if name not in manager.modules:
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"Module '{name}' not found")

        try:
            await manager.enable_module(name)
            return {"success": True, "module": name, "enabled": True}
        except Exception as e:
            logger.error(f"Failed to enable {name}: {e}")
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e)) from e

    @router.post("/modules/{name}/disable")
    async def disable_module(name: str, request: Request) -> dict:
        """Disable an enabled module"""
        manager = get_manager(request)

        if name not in manager.modules:
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"Module '{name}' not found")

        try:
            await manager.disable_module(name)
            return {"success": True, "module": name, "enabled": False}
        except Exception as e:
            logger.error(f"Failed to disable {name}: {e}")
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e)) from e

    return router
