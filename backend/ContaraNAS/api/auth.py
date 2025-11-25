from backend.ContaraNAS.core.utils import get_logger
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .requests import PairRequest
from .responses import PairingStatusResponse, PairResponse, VerifyResponse


logger = get_logger(__name__)

# Bearer token security scheme
bearer_scheme = HTTPBearer(auto_error=False)


def get_auth_service(request: Request):
    """Get auth service from app state"""
    return request.app.state.auth_service


def require_auth(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> None:
    """Dependency that validates the bearer token - Protects endpoints that require authentication"""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    auth_service = get_auth_service(request)

    if not auth_service.verify_token(credentials.credentials):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def create_auth_routes() -> APIRouter:
    """Create API router for authentication endpoints"""
    router = APIRouter(prefix="/api/auth", tags=["authentication"])

    @router.post("/pair", response_model=PairResponse)
    async def pair(request: Request, pair_request: PairRequest) -> PairResponse:
        """Exchange a pairing code for an API token"""
        auth_service = get_auth_service(request)

        try:
            api_token = auth_service.pair(pair_request.pairing_code)
        except RuntimeError as e:
            raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, str(e)) from e
        except ValueError as e:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, str(e)) from e

        return PairResponse(
            success=True,
            api_token=api_token,
            message="Paired successfully. Store this token securely.",
        )

    @router.get("/status", response_model=PairingStatusResponse)
    async def get_pairing_status(request: Request) -> PairingStatusResponse:
        """Get current pairing status"""
        auth_service = get_auth_service(request)
        active_pairing = auth_service.get_active_pairing_info()

        return PairingStatusResponse(
            is_paired=auth_service.is_paired(),
            locked_out=auth_service.is_locked_out(),
            lockout_remaining_seconds=auth_service.get_lockout_remaining(),
            active_pairing_expires_in=active_pairing["expires_in_seconds"]
            if active_pairing
            else None,
        )

    @router.get("/verify", response_model=VerifyResponse)
    async def verify_token(
        request: Request,
        credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    ) -> VerifyResponse:
        """Verify if a token is valid"""
        if credentials is None:
            return VerifyResponse(valid=False)

        auth_service = get_auth_service(request)
        valid = auth_service.verify_token(credentials.credentials)

        return VerifyResponse(valid=valid)

    return router
