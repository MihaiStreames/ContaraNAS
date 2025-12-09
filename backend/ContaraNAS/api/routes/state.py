from fastapi import APIRouter, Depends, Request

from ContaraNAS.api.responses import AppStateResponse, ModuleSnapshot
from ContaraNAS.core.utils import get_logger

from .auth import require_auth


logger = get_logger(__name__)


def create_state_routes() -> APIRouter:
    """Create API router for app state endpoints"""
    router = APIRouter(prefix="/api", tags=["state"])

    def get_manager(request: Request):
        """Extract module manager from app state"""
        return request.app.state.module_manager

    @router.get("/state", response_model=AppStateResponse)
    async def get_app_state(
        request: Request,
        _: None = Depends(require_auth),
    ) -> AppStateResponse:
        """Get full application state"""
        manager = get_manager(request)

        modules = []
        for name, module in manager.modules.items():
            ui = None
            if module.enable_flag:
                ui = module.render_ui()

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
