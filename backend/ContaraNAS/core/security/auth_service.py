from dataclasses import dataclass
import hashlib
import secrets
import time

from backend.ContaraNAS.core.utils import get_cache_dir, get_logger, load_json, save_json


logger = get_logger(__name__)

# Pairing code format
PAIRING_CODE_SEGMENT_LENGTH = 4
PAIRING_CODE_SEGMENTS = 3
PAIRING_CODE_LENGTH = PAIRING_CODE_SEGMENT_LENGTH * PAIRING_CODE_SEGMENTS

# Token settings
API_TOKEN_LENGTH = 64  # 256-bit tokens


@dataclass
class PairingConfig:
    """Configuration for pairing service"""

    token_validity_seconds: int = 300
    max_failed_attempts: int = 5
    lockout_duration_seconds: int = 300
    enabled: bool = True


@dataclass
class PairingToken:
    """Active pairing token"""

    raw_token: str
    display_token: str
    created_at: float
    expires_at: float
    used: bool = False


@dataclass
class RegisteredDevice:
    """A paired device"""

    name: str
    token_hash: str
    created_at: float
    last_seen: float | None = None


@dataclass
class AuthState:
    """Authentication state"""

    failed_attempts: int = 0
    lockout_until: float = 0
    active_pairing: PairingToken | None = None


class AuthService:
    """Manages device pairing and API token authentication"""

    def __init__(self, config: PairingConfig | None = None):
        self.config = config or PairingConfig()
        self._state = AuthState()
        self._devices_file = get_cache_dir() / "security" / "devices.json"
        self._devices: dict[str, RegisteredDevice] = {}
        self._load_devices()

    def is_enabled(self) -> bool:
        """Check if pairing is enabled"""
        return self.config.enabled

    def is_locked_out(self) -> bool:
        """Check if pairing is locked out due to failed attempts"""
        if self._state.lockout_until > time.time():
            return True
        if self._state.lockout_until > 0:
            self._state.lockout_until = 0
            self._state.failed_attempts = 0
        return False

    def get_lockout_remaining(self) -> int:
        """Get remaining lockout seconds"""
        if not self.is_locked_out():
            return 0
        return int(self._state.lockout_until - time.time())

    def generate_pairing_code(self) -> str:
        """Generate a new pairing code and display it on stdout"""
        if not self.config.enabled:
            raise RuntimeError("Pairing is disabled")

        if self.is_locked_out():
            remaining = self.get_lockout_remaining()
            raise RuntimeError(f"Pairing locked out. Try again in {remaining} seconds.")

        # Generate cryptographically secure random token
        raw_token = secrets.token_hex(PAIRING_CODE_LENGTH // 2)[:PAIRING_CODE_LENGTH]

        # Format for display: XXXX-XXXX-XXXX
        display_token = "-".join(
            raw_token[i : i + PAIRING_CODE_SEGMENT_LENGTH].upper()
            for i in range(0, PAIRING_CODE_LENGTH, PAIRING_CODE_SEGMENT_LENGTH)
        )

        now = time.time()
        self._state.active_pairing = PairingToken(
            raw_token=raw_token.lower(),
            display_token=display_token,
            created_at=now,
            expires_at=now + self.config.token_validity_seconds,
        )

        self._display_pairing_code(display_token)
        return display_token

    def get_active_pairing_info(self) -> dict | None:
        """Get info about active pairing (for admin UI)"""
        if self._state.active_pairing is None:
            return None

        active = self._state.active_pairing
        now = time.time()

        if now > active.expires_at or active.used:
            return None

        return {
            "display_token": active.display_token,
            "expires_in_seconds": int(active.expires_at - now),
        }

    def cancel_pairing(self) -> bool:
        """Cancel any active pairing"""
        if self._state.active_pairing is not None:
            self._state.active_pairing = None
            logger.info("Active pairing cancelled")
            return True
        return False

    def pair_device(self, pairing_code: str, device_name: str) -> str:
        """Exchange a pairing code for an API token"""
        if not self.config.enabled:
            raise RuntimeError("Pairing is disabled")

        if self.is_locked_out():
            remaining = self.get_lockout_remaining()
            raise RuntimeError(f"Pairing locked out. Try again in {remaining} seconds.")

        # Normalize code
        normalized = pairing_code.replace("-", "").replace(" ", "").lower()

        # Validate pairing code
        if not self._verify_pairing_code(normalized):
            self._record_failed_attempt()
            raise ValueError("Invalid or expired pairing code")

        # Check device name
        if device_name in self._devices:
            raise ValueError(f"Device '{device_name}' already exists. Delete it first.")

        # Generate API token
        api_token = secrets.token_urlsafe(API_TOKEN_LENGTH)
        token_hash = self._hash_token(api_token)

        # Register device
        self._devices[device_name] = RegisteredDevice(
            name=device_name,
            token_hash=token_hash,
            created_at=time.time(),
        )
        self._save_devices()

        # Consume pairing code
        self._state.active_pairing.used = True
        self._state.active_pairing = None
        self._state.failed_attempts = 0

        logger.info(f"Device paired successfully: {device_name}")
        return api_token

    def _verify_pairing_code(self, normalized_code: str) -> bool:
        """Verify a pairing code"""
        if self._state.active_pairing is None:
            return False

        active = self._state.active_pairing

        if time.time() > active.expires_at:
            logger.warning("Pairing attempt with expired code")
            self._state.active_pairing = None
            return False

        if active.used:
            logger.warning("Pairing attempt with used code")
            return False

        # Constant-time comparison
        return secrets.compare_digest(normalized_code, active.raw_token)

    def verify_token(self, token: str) -> str | None:
        """Verify an API token"""
        token_hash = self._hash_token(token)

        for device_name, device in self._devices.items():
            if secrets.compare_digest(device.token_hash, token_hash):
                # Update last seen
                device.last_seen = time.time()
                self._save_devices()
                return device_name

        return None

    def is_authenticated(self, token: str | None) -> bool:
        """Check if a token is valid"""
        if not token:
            return False
        return self.verify_token(token) is not None

    def list_devices(self) -> list[dict]:
        """List all paired devices"""
        return [
            {
                "name": d.name,
                "created_at": d.created_at,
                "last_seen": d.last_seen,
            }
            for d in self._devices.values()
        ]

    def get_device(self, name: str) -> dict | None:
        """Get info about a specific device"""
        device = self._devices.get(name)
        if not device:
            return None
        return {
            "name": device.name,
            "created_at": device.created_at,
            "last_seen": device.last_seen,
        }

    def delete_device(self, name: str) -> bool:
        """Delete a paired device (revokes its token)"""
        if name in self._devices:
            del self._devices[name]
            self._save_devices()
            logger.info(f"Device deleted: {name}")
            return True
        return False

    def has_devices(self) -> bool:
        """Check if any devices are paired"""
        return len(self._devices) > 0

    @staticmethod
    def _hash_token(token: str) -> str:
        """Hash a token for storage"""
        return hashlib.sha256(token.encode()).hexdigest()

    def _record_failed_attempt(self) -> None:
        """Record failed attempt and lock out if threshold reached"""
        self._state.failed_attempts += 1
        logger.warning(
            f"Failed pairing attempt {self._state.failed_attempts}/{self.config.max_failed_attempts}"
        )

        if self._state.failed_attempts >= self.config.max_failed_attempts:
            self._state.lockout_until = time.time() + self.config.lockout_duration_seconds
            self._state.active_pairing = None
            logger.error(
                f"Pairing locked out for {self.config.lockout_duration_seconds}s "
                f"after {self._state.failed_attempts} failed attempts"
            )

    def _save_devices(self) -> None:
        """Save devices to disk"""
        self._devices_file.parent.mkdir(parents=True, exist_ok=True)
        data = {
            name: {
                "name": d.name,
                "token_hash": d.token_hash,
                "created_at": d.created_at,
                "last_seen": d.last_seen,
            }
            for name, d in self._devices.items()
        }
        save_json(self._devices_file, data)

    def _load_devices(self) -> None:
        """Load devices from disk"""
        data = load_json(self._devices_file)
        if data:
            self._devices = {name: RegisteredDevice(**info) for name, info in data.items()}
            logger.info(f"Loaded {len(self._devices)} paired devices")

    @staticmethod
    def _display_pairing_code(code: str) -> None:
        """Display pairing code on stdout"""
        print()
        print("╔══════════════════════════════════════════════════╗")
        print("║          CONTARANAS PAIRING CODE                 ║")
        print("╠══════════════════════════════════════════════════╣")
        print("║                                                  ║")
        print(f"║{code.center(50)}║")
        print("║                                                  ║")
        print("╠══════════════════════════════════════════════════╣")
        print("║  Enter this code in the ContaraNAS app to pair   ║")
        print("║  This code expires in 5 minutes                  ║")
        print("╚══════════════════════════════════════════════════╝")
        print()
        logger.info(f"Pairing code generated: {code}")
