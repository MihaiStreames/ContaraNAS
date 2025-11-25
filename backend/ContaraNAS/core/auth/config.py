from dataclasses import dataclass


@dataclass
class PairingConfig:
    """Configuration for pairing service"""

    token_validity_seconds: int = 300
    max_failed_attempts: int = 5
    lockout_duration_seconds: int = 300
    enabled: bool = True
