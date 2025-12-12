from fastapi import APIRouter
from fastapi import Depends
from fastapi import Request

from ContaraNAS.core import get_logger

from ..responses import AppStateResponse
from ..responses import ModuleSnapshot
from .auth import require_auth
from .commands import _get_manager


logger = get_logger(__name__)


def create_state_routes() -> APIRouter:
    """Create API router for app state endpoints"""
    router = APIRouter(prefix="/api", tags=["state"])

    @router.get("/state", response_model=AppStateResponse)
    async def get_app_state(
        request: Request,
        _: None = Depends(require_auth),
    ) -> AppStateResponse:
        """Get full application state"""
        manager = _get_manager(request)

        modules = []
        for name, module in manager.modules.items():
            # Always render UI even for disabled modules (shows last known state)
            ui = module.render_ui() if module.init_flag else None

            modules.append(
                ModuleSnapshot(
                    name=name,
                    display_name=module.display_name,
                    enabled=module.enable_flag,
                    initialized=module.init_flag,
                    ui=ui,
                )
            )

        return AppStateResponse(
            modules=modules,
            active_modal=None,
        )

    return router
