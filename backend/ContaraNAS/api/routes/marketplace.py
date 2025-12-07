from ContaraNAS.api.routes.auth import require_auth
from ContaraNAS.core.exceptions import ChecksumMismatchError, MarketplaceError
from ContaraNAS.core.utils import get_logger
from fastapi import APIRouter, Depends, HTTPException, Request


logger = get_logger(__name__)


def create_marketplace_routes() -> APIRouter:
    """Create API router for marketplace endpoints"""
    router = APIRouter(prefix="/api/marketplace", tags=["marketplace"])

    def get_client(request: Request):
        """Get marketplace client from app state"""
        client = getattr(request.app.state, "marketplace_client", None)
        if client is None:
            raise HTTPException(
                status_code=503,
                detail="Marketplace not configured",
            )
        return client

    @router.get("/modules")
    async def list_modules(
        request: Request,
        _: None = Depends(require_auth),
    ):
        """List all available modules from marketplace"""
        client = get_client(request)

        try:
            registry = await client.get_registry()
            return {
                "modules": registry.get("modules", {}),
                "checksum": registry.get("checksum"),
            }

        except ChecksumMismatchError as e:
            logger.error(f"Registry checksum failed: {e}")
            raise HTTPException(
                status_code=502,
                detail="Marketplace data integrity check failed",
            ) from e

        except MarketplaceError as e:
            logger.error(f"Marketplace error: {e}")
            raise HTTPException(
                status_code=502,
                detail=str(e),
            ) from e

    @router.get("/modules/{module_id}")
    async def get_module(
        module_id: str,
        request: Request,
        _: None = Depends(require_auth),
    ):
        """Get detailed information about a specific module"""
        client = get_client(request)

        try:
            module = await client.get_module(module_id)

            if module is None:
                raise HTTPException(
                    status_code=404,
                    detail=f"Module '{module_id}' not found or no compatible versions",
                )

            return {"module": module}

        except MarketplaceError as e:
            logger.error(f"Failed to fetch module {module_id}: {e}")
            raise HTTPException(
                status_code=502,
                detail=str(e),
            ) from e

    @router.post("/refresh")
    async def refresh_registry(
        request: Request,
        _: None = Depends(require_auth),
    ):
        """Force refresh the marketplace registry cache"""
        client = get_client(request)

        try:
            registry = await client.get_registry(force_refresh=True)
            module_count = len(registry.get("modules", {}))

            return {
                "success": True,
                "message": f"Registry refreshed: {module_count} modules available",
            }

        except MarketplaceError as e:
            logger.error(f"Failed to refresh registry: {e}")
            raise HTTPException(
                status_code=502,
                detail=str(e),
            ) from e

    return router
