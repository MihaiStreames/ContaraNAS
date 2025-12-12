from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status

from ContaraNAS.api.responses import (
    ModuleModalsResponse,
    ModuleTileResponse,
    ModuleUIResponse,
)
from ContaraNAS.core.action import ActionDispatcher
from ContaraNAS.core.exceptions import ActionError
from ContaraNAS.core.module import Module
from ContaraNAS.core import get_logger

from .auth import require_auth
from .commands import _get_manager


logger = get_logger(__name__)


def _get_enabled_module(request: Request, name: str) -> Module:
    """Get an enabled module by name"""
    manager = _get_manager(request)

    if name not in manager.modules:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Module '{name}' not found")

    module = manager.modules[name]

    if not module.enable_flag:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Module '{name}' is not enabled")

    return module


def _get_dispatcher(request: Request) -> ActionDispatcher:
    """Extract action dispatcher from app state"""
    return request.app.state.action_dispatcher


def create_module_routes() -> APIRouter:
    """Create API router for module UI and action endpoints"""
    router = APIRouter(prefix="/api/modules", tags=["modules"])

    @router.get("/{name}/ui", response_model=ModuleUIResponse)
    async def get_module_ui(
        name: str,
        request: Request,
        _: None = Depends(require_auth),
    ) -> ModuleUIResponse:
        """Get full UI for a module"""
        module = _get_enabled_module(request, name)
        return ModuleUIResponse(module=name, ui=module.render_ui())

    @router.get("/{name}/tile", response_model=ModuleTileResponse)
    async def get_module_tile(
        name: str,
        request: Request,
        _: None = Depends(require_auth),
    ) -> ModuleTileResponse:
        """Get only the tile for a module"""
        module = _get_enabled_module(request, name)
        return ModuleTileResponse(module=name, tile=module.render_tile())

    @router.get("/{name}/modals", response_model=ModuleModalsResponse)
    async def get_module_modals(
        name: str,
        request: Request,
        _: None = Depends(require_auth),
    ) -> ModuleModalsResponse:
        """Get only the modals for a module"""
        module = _get_enabled_module(request, name)
        return {"module": name, "modals": module.render_modals()}

    @router.post("/{name}/action/{action_name}")
    async def invoke_action(
        name: str,
        action_name: str,
        request: Request,
        _: None = Depends(require_auth),
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Invoke an action on a module"""
        _get_enabled_module(request, name)
        dispatcher = _get_dispatcher(request)

        try:
            # catch_errors=True means action exceptions become error notifications
            results = await dispatcher.dispatch(name, action_name, payload, catch_errors=True)
            return {"success": True, "module": name, "action": action_name, "results": results}

        except ActionError as e:
            # Infrastructure errors (module/action not found)
            logger.error(f"Action error: {e}")
            raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e)) from e

    @router.get("/{name}/actions")
    async def list_module_actions(
        name: str,
        request: Request,
        _: None = Depends(require_auth),
    ) -> dict[str, Any]:
        """List available actions for a module"""
        manager = _get_manager(request)

        if name not in manager.modules:
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"Module '{name}' not found")

        dispatcher = _get_dispatcher(request)
        return {"module": name, "actions": dispatcher.get_module_actions(name)}

    return router
