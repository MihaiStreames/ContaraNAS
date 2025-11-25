from backend.ContaraNAS.core.utils import get_logger
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel


logger = get_logger(__name__)

# Bearer token security scheme
bearer_scheme = HTTPBearer(auto_error=False)


class PairRequest(BaseModel):
    """Request to pair a new device"""

    pairing_code: str
    device_name: str


class PairResponse(BaseModel):
    """Response containing API token"""

    success: bool
    device_name: str
    api_token: str
    message: str


class GenerateCodeResponse(BaseModel):
    """Response when generating a pairing code"""

    success: bool
    pairing_code: str
    expires_in_seconds: int


class DeviceInfo(BaseModel):
    """Information about a paired device"""

    name: str
    created_at: float
    last_seen: float | None


class DeviceListResponse(BaseModel):
    """Response listing all devices"""

    devices: list[DeviceInfo]
    total: int


def get_auth_service(request: Request):
    """Get auth service from app state"""
    return request.app.state.auth_service


def get_current_device(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> str:
    """
    Dependency that validates the bearer token and returns the device name.
    Use this to protect endpoints that require authentication.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    auth_service = get_auth_service(request)
    device_name = auth_service.verify_token(credentials.credentials)

    if device_name is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return device_name


def get_optional_device(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> str | None:
    """
    Dependency that optionally validates token.
    Returns device name if authenticated, None otherwise.
    """
    if credentials is None:
        return None

    auth_service = get_auth_service(request)
    return auth_service.verify_token(credentials.credentials)


def create_auth_routes() -> APIRouter:
    """Create API router for authentication endpoints"""
    router = APIRouter(prefix="/api/auth", tags=["authentication"])

    @router.post("/generate-code", response_model=GenerateCodeResponse)
    async def generate_pairing_code(request: Request) -> GenerateCodeResponse:
        """Generate a new pairing code for device enrollment"""
        auth_service = get_auth_service(request)

        try:
            code = auth_service.generate_pairing_code()
            info = auth_service.get_active_pairing_info()

            return GenerateCodeResponse(
                success=True,
                pairing_code=code,
                expires_in_seconds=info["expires_in_seconds"] if info else 0,
            )
        except RuntimeError as e:
            raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, str(e)) from e

    @router.post("/pair", response_model=PairResponse)
    async def pair_device(request: Request, pair_request: PairRequest) -> PairResponse:
        """Exchange a pairing code for an API token"""
        auth_service = get_auth_service(request)

        try:
            api_token = auth_service.pair_device(
                pair_request.pairing_code,
                pair_request.device_name,
            )
        except RuntimeError as e:
            raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, str(e)) from e
        except ValueError as e:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, str(e)) from e

        return PairResponse(
            success=True,
            device_name=pair_request.device_name,
            api_token=api_token,
            message="Device paired successfully. Store this token securely.",
        )

    @router.get("/pairing-status")
    async def get_pairing_status(request: Request) -> dict:
        """Get current pairing status"""
        auth_service = get_auth_service(request)

        return {
            "enabled": auth_service.is_enabled(),
            "locked_out": auth_service.is_locked_out(),
            "lockout_remaining_seconds": auth_service.get_lockout_remaining(),
            "active_pairing": auth_service.get_active_pairing_info(),
            "has_paired_devices": auth_service.has_devices(),
        }

    @router.post("/cancel-pairing")
    async def cancel_pairing(request: Request) -> dict:
        """Cancel any active pairing code"""
        auth_service = get_auth_service(request)

        cancelled = auth_service.cancel_pairing()
        return {
            "success": cancelled,
            "message": "Pairing cancelled" if cancelled else "No active pairing",
        }

    @router.get("/verify")
    async def verify_token(
        request: Request,
        credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    ) -> dict:
        """Verify if a token is valid"""
        if credentials is None:
            return {"valid": False, "device": None}

        auth_service = get_auth_service(request)
        device = auth_service.verify_token(credentials.credentials)

        return {"valid": device is not None, "device": device}

    @router.get("/devices", response_model=DeviceListResponse)
    async def list_devices(
        request: Request,
        _current_device: str = Depends(get_current_device),
    ) -> DeviceListResponse:
        """List all paired devices (requires authentication)"""
        auth_service = get_auth_service(request)
        devices = auth_service.list_devices()

        return DeviceListResponse(
            devices=[DeviceInfo(**d) for d in devices],
            total=len(devices),
        )

    @router.get("/devices/{device_name}", response_model=DeviceInfo)
    async def get_device(
        request: Request,
        device_name: str,
        _current_device: str = Depends(get_current_device),
    ) -> DeviceInfo:
        """Get info about a specific device"""
        auth_service = get_auth_service(request)
        device = auth_service.get_device(device_name)

        if device is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"Device '{device_name}' not found")

        return DeviceInfo(**device)

    @router.delete("/devices/{device_name}")
    async def delete_device(
        request: Request,
        device_name: str,
        current_device: str = Depends(get_current_device),
    ) -> dict:
        """Delete a paired device (revokes its token)"""
        # Prevent deleting yourself
        if device_name == current_device:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                "Cannot delete your own device. Use another device to remove this one.",
            )

        auth_service = get_auth_service(request)

        if not auth_service.delete_device(device_name):
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"Device '{device_name}' not found")

        return {"success": True, "message": f"Device '{device_name}' has been deleted"}

    @router.get("/me")
    async def get_current_device_info(
        request: Request,
        current_device: str = Depends(get_current_device),
    ) -> DeviceInfo:
        """Get info about the currently authenticated device"""
        auth_service = get_auth_service(request)
        device = auth_service.get_device(current_device)

        if device is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Device not found")

        return DeviceInfo(**device)

    return router
