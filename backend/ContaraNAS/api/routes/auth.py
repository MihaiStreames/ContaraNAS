import contextlib
from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request
from fastapi import status
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.security import HTTPBearer

from ContaraNAS.core import get_logger
from ContaraNAS.core.auth import AuthService
from ContaraNAS.core.exceptions import PairingError

from ..requests import PairRequest
from ..responses import PairResponse
from ..responses import SuccessResponse


logger = get_logger(__name__)

bearer_scheme = HTTPBearer(auto_error=False)
BearerCredentials = Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)]


def _get_auth_service(request: Request) -> AuthService:
    """Extract auth service from app state"""
    return request.app.state.auth_service


def require_auth(
    request: Request,
    credentials: BearerCredentials,
) -> None:
    """Dependency that validates the bearer token"""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    auth_service = _get_auth_service(request)

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
        auth_service = _get_auth_service(request)

        try:
            api_token = auth_service.pair(pair_request.pairing_code)

        except PairingError as e:
            raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, str(e)) from e
        except ValueError as e:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, str(e)) from e

        return PairResponse(
            success=True,
            api_token=api_token,
            message="Paired successfully",
        )

    @router.post("/unpair", response_model=SuccessResponse)
    async def unpair(
        request: Request,
        _: None = Depends(require_auth),
    ) -> SuccessResponse:
        """Unpair the app from this NAS"""
        auth_service = _get_auth_service(request)
        auth_service.unpair()

        # Generate a new pairing code even if unpairing fails
        # to avoid leaving the NAS without a valid pairing code
        with contextlib.suppress(PairingError):
            auth_service.generate_pairing_code()

        return SuccessResponse(success=True, message="Unpaired successfully")

    return router
