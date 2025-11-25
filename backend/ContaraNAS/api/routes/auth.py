from backend.ContaraNAS.api.requests import PairRequest
from backend.ContaraNAS.api.responses import PairResponse, SuccessResponse
from backend.ContaraNAS.core.utils import get_logger
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer


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


def extract_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> str | None:
    """Extract bearer token from request"""
    if credentials is None:
        return None
    return credentials.credentials


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

    @router.post("/unpair", response_model=SuccessResponse)
    async def unpair(
        request: Request,
        _: None = Depends(require_auth),
    ) -> SuccessResponse:
        """Unpair the app from this NAS. Requires authentication"""
        auth_service = get_auth_service(request)
        auth_service.unpair()

        # Generate a new pairing code for next pairing
        try:
            auth_service.generate_pairing_code()
        except RuntimeError:
            pass  # Code generation failed, but unpair succeeded

        return SuccessResponse(success=True, message="Unpaired successfully")

    return router
