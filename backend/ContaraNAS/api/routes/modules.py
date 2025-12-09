from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status

from ContaraNAS.api.responses import (
    ActionListResponse,
    ActionResultResponse,
    ModuleModalsResponse,
    ModuleTileResponse,
    ModuleUIResponse,
)
from ContaraNAS.core.action import ActionDispatcher
from ContaraNAS.core.exceptions import ActionError
from ContaraNAS.core.utils import get_logger

from .auth import require_auth


logger = get_logger(__name__)


def create_module_routes() -> APIRouter:
    """Create API router for module UI and action endpoints"""
    router = APIRouter(prefix="/api/modules", tags=["modules"])

    def get_manager(request: Request):
        """Extract module manager from app state"""
        return request.app.state.module_manager

    def get_dispatcher(request: Request) -> ActionDispatcher:
        """Extract action dispatcher from app state"""
        return request.app.state.action_dispatcher

    @router.get("/{name}/ui", response_model=ModuleUIResponse)
    async def get_module_ui(
        name: str,
        request: Request,
        _: None = Depends(require_auth),
    ) -> ModuleUIResponse:
        """Get full UI for a module (tile + modals)"""
        manager = get_manager(request)

        if name not in manager.modules:
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"Module '{name}' not found")

        module = manager.modules[name]

        if not module.enable_flag:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Module '{name}' is not enabled")

        return ModuleUIResponse(module=name, ui=module.render_ui())

    @router.get("/{name}/tile", response_model=ModuleTileResponse)
    async def get_module_tile(
        name: str,
        request: Request,
        _: None = Depends(require_auth),
    ) -> ModuleTileResponse:
        """Get just the tile for a module"""
        manager = get_manager(request)

        if name not in manager.modules:
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"Module '{name}' not found")

        module = manager.modules[name]

        if not module.enable_flag:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Module '{name}' is not enabled")

        return ModuleTileResponse(module=name, tile=module.render_tile())

    @router.get("/{name}/modals", response_model=ModuleModalsResponse)
    async def get_module_modals(
        name: str,
        request: Request,
        _: None = Depends(require_auth),
    ) -> ModuleModalsResponse:
        """Get just the modals for a module"""
        manager = get_manager(request)

        if name not in manager.modules:
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"Module '{name}' not found")

        module = manager.modules[name]

        if not module.enable_flag:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Module '{name}' is not enabled")

        return {
            "module": name,
            "modals": module.render_modals(),
        }

    @router.post("/{name}/action/{action_name}")
    async def invoke_action(
        name: str,
        action_name: str,
        request: Request,
        _: None = Depends(require_auth),
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Invoke an action on a module"""
        manager = get_manager(request)

        if name not in manager.modules:
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"Module '{name}' not found")

        module = manager.modules[name]

        if not module.enable_flag:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Module '{name}' is not enabled")

        dispatcher = get_dispatcher(request)

        try:
            results = await dispatcher.dispatch(name, action_name, payload)
            return {
                "success": True,
                "module": name,
                "action": action_name,
                "results": results,
            }
        except ActionError as e:
            logger.error(f"Action error: {e}")
            raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e)) from e
        except Exception as e:
            logger.exception(f"Unexpected error invoking action {name}.{action_name}")
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Action failed: {e}") from e

    @router.get("/{name}/actions")
    async def list_module_actions(
        name: str,
        request: Request,
        _: None = Depends(require_auth),
    ) -> dict[str, Any]:
        """List available actions for a module"""
        manager = get_manager(request)

        if name not in manager.modules:
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"Module '{name}' not found")

        dispatcher = get_dispatcher(request)
        actions = dispatcher.get_module_actions(name)

        return {
            "module": name,
            "actions": actions,
        }

    return router
