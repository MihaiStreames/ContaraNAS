import hashlib
import secrets
import time

from backend.ContaraNAS.core import settings
from backend.ContaraNAS.core.utils import get_logger, load_json, save_json

from .config import PairingConfig
from .models import AuthState, PairedApp, PairingToken


logger = get_logger(__name__)

# Pairing code format
PAIRING_CODE_SEGMENT_LENGTH = 4
PAIRING_CODE_SEGMENTS = 3
PAIRING_CODE_LENGTH = PAIRING_CODE_SEGMENT_LENGTH * PAIRING_CODE_SEGMENTS

# Token settings
API_TOKEN_LENGTH = 64  # 256-bit tokens


class AuthService:
    """Manages app pairing and API token authentication - One NAS can only be paired with one app"""

    def __init__(self, config: PairingConfig | None = None):
        self.config = config or PairingConfig()
        self._state = AuthState()
        self._paired_app_file = settings.cache_dir / "security" / "paired_app.json"
        self._paired_app: PairedApp | None = None
        self._load_paired_app()

    def is_enabled(self) -> bool:
        """Check if pairing is enabled"""
        return self.config.enabled

    def is_paired(self) -> bool:
        """Check if an app is already paired"""
        return self._paired_app is not None

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

        if self.is_paired():
            raise RuntimeError("Already paired with an app. Unpair first to generate new code.")

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

    def pair(self, pairing_code: str) -> str:
        """Exchange a pairing code for an API token"""
        if not self.config.enabled:
            raise RuntimeError("Pairing is disabled")

        if self.is_paired():
            raise RuntimeError("Already paired with an app")

        if self.is_locked_out():
            remaining = self.get_lockout_remaining()
            raise RuntimeError(f"Pairing locked out. Try again in {remaining} seconds.")

        # Normalize code
        normalized = pairing_code.replace("-", "").replace(" ", "").lower()

        # Validate pairing code
        if not self._verify_pairing_code(normalized):
            self._record_failed_attempt()
            raise ValueError("Invalid or expired pairing code")

        # Generate API token
        api_token = secrets.token_urlsafe(API_TOKEN_LENGTH)
        token_hash = self._hash_token(api_token)

        # Store paired app
        self._paired_app = PairedApp(
            token_hash=token_hash,
            paired_at=time.time(),
        )
        self._save_paired_app()

        # Consume pairing code
        self._state.active_pairing.used = True
        self._state.active_pairing = None
        self._state.failed_attempts = 0

        logger.info("App paired successfully")
        return api_token

    def unpair(self) -> bool:
        """Unpair the current app. Returns True if was paired"""
        if self._paired_app is None:
            return False

        self._paired_app = None
        self._save_paired_app()
        logger.info("App unpaired")
        return True

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

    def verify_token(self, token: str) -> bool:
        """Verify an API token"""
        if self._paired_app is None:
            return False

        token_hash = self._hash_token(token)

        if secrets.compare_digest(self._paired_app.token_hash, token_hash):
            # Update last seen
            self._paired_app.last_seen = time.time()
            self._save_paired_app()
            return True

        return False

    def is_authenticated(self, token: str | None) -> bool:
        """Check if a token is valid"""
        if not token:
            return False
        return self.verify_token(token)

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

    def _save_paired_app(self) -> None:
        """Save paired app to disk"""
        self._paired_app_file.parent.mkdir(parents=True, exist_ok=True)

        if self._paired_app is None:
            # Delete the file if unpaired
            if self._paired_app_file.exists():
                self._paired_app_file.unlink()
            return

        data = {
            "token_hash": self._paired_app.token_hash,
            "paired_at": self._paired_app.paired_at,
            "last_seen": self._paired_app.last_seen,
        }
        save_json(self._paired_app_file, data)

    def _load_paired_app(self) -> None:
        """Load paired app from disk"""
        data = load_json(self._paired_app_file)
        if data:
            self._paired_app = PairedApp(
                token_hash=data["token_hash"],
                paired_at=data["paired_at"],
                last_seen=data.get("last_seen"),
            )
            logger.info("Loaded paired app configuration")

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
