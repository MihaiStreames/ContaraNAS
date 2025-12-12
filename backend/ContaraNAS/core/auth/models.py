import msgspec


class PairingToken(msgspec.Struct):
    """Active pairing token"""

    raw_token: str
    display_token: str
    created_at: float
    expires_at: float
    used: bool = False


class PairedApp(msgspec.Struct, gc=False):
    """The single paired app"""

    token_hash: str
    paired_at: float
    last_seen: float | None = None


class AuthState(msgspec.Struct):
    """Authentication state"""

    failed_attempts: int = 0
    lockout_until: float = 0.0
    active_pairing: PairingToken | None = None
