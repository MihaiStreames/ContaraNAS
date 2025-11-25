from dataclasses import dataclass


@dataclass
class PairingToken:
    """Active pairing token"""

    raw_token: str
    display_token: str
    created_at: float
    expires_at: float
    used: bool = False


@dataclass
class PairedApp:
    """The single paired app"""

    token_hash: str
    paired_at: float
    last_seen: float | None = None


@dataclass
class AuthState:
    """Authentication state"""

    failed_attempts: int = 0
    lockout_until: float = 0
    active_pairing: PairingToken | None = None
