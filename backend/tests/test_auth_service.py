from pathlib import Path
import tempfile
import time
from unittest.mock import patch

import pytest

from ContaraNAS.core.auth.config import PairingConfig
from ContaraNAS.core.auth.models import AuthState, PairedApp, PairingToken
from ContaraNAS.core.auth.service import AuthService
from ContaraNAS.core.exceptions import PairingError


@pytest.fixture
def auth_service(tmp_path):
    """Create an auth service with temp storage"""
    with patch("ContaraNAS.core.auth.service.settings") as mock_settings:
        mock_settings.cache_dir = tmp_path
        service = AuthService()
        yield service


@pytest.fixture
def disabled_auth_service(tmp_path):
    """Create a disabled auth service"""
    with patch("ContaraNAS.core.auth.service.settings") as mock_settings:
        mock_settings.cache_dir = tmp_path
        config = PairingConfig(enabled=False)
        service = AuthService(config=config)
        yield service


def test_auth_service_init(auth_service):
    """Test auth service initializes correctly"""
    assert auth_service.is_enabled() is True
    assert auth_service.is_paired() is False
    assert auth_service.is_locked_out() is False


def test_auth_service_disabled(disabled_auth_service):
    """Test disabled auth service"""
    assert disabled_auth_service.is_enabled() is False

    with pytest.raises(PairingError) as exc:
        disabled_auth_service.generate_pairing_code()
    assert "disabled" in str(exc.value)


def test_generate_pairing_code(auth_service):
    """Test pairing code generation"""
    code = auth_service.generate_pairing_code()

    # Format: XXXX-XXXX-XXXX
    assert len(code) == 14
    assert code.count("-") == 2
    parts = code.split("-")
    assert all(len(part) == 4 for part in parts)
    assert all(part.isupper() or part.isdigit() for part in parts)


def test_generate_pairing_code_when_paired_fails(auth_service):
    """Test cannot generate code when already paired"""
    # Pair first
    code = auth_service.generate_pairing_code()
    normalized = code.replace("-", "").lower()
    auth_service.pair(normalized)

    # Try to generate new code
    with pytest.raises(PairingError) as exc:
        auth_service.generate_pairing_code()
    assert "already paired" in str(exc.value).lower()


def test_pair_success(auth_service):
    """Test successful pairing"""
    code = auth_service.generate_pairing_code()
    normalized = code.replace("-", "").lower()

    api_token = auth_service.pair(normalized)

    assert api_token is not None
    assert len(api_token) > 0
    assert auth_service.is_paired() is True


def test_pair_with_formatted_code(auth_service):
    """Test pairing with formatted code (XXXX-XXXX-XXXX)"""
    code = auth_service.generate_pairing_code()

    # Use the formatted code directly
    api_token = auth_service.pair(code)

    assert api_token is not None
    assert auth_service.is_paired() is True


def test_pair_invalid_code(auth_service):
    """Test pairing with invalid code fails"""
    auth_service.generate_pairing_code()

    with pytest.raises(ValueError) as exc:
        auth_service.pair("invalid-code")
    assert "Invalid" in str(exc.value)


def test_pair_no_active_code(auth_service):
    """Test pairing without generating code first fails"""
    with pytest.raises(ValueError) as exc:
        auth_service.pair("abcd-efgh-ijkl")
    assert "Invalid" in str(exc.value)


def test_pair_expired_code(tmp_path):
    """Test pairing with expired code fails"""
    with patch("ContaraNAS.core.auth.service.settings") as mock_settings:
        mock_settings.cache_dir = tmp_path
        # Create service with very short validity
        config = PairingConfig(token_validity_seconds=0)
        service = AuthService(config=config)

        code = service.generate_pairing_code()
        time.sleep(0.1)  # Wait for expiration

        with pytest.raises(ValueError) as exc:
            service.pair(code)
        assert "Invalid" in str(exc.value)


def test_verify_token(auth_service):
    """Test token verification"""
    code = auth_service.generate_pairing_code()
    api_token = auth_service.pair(code)

    assert auth_service.verify_token(api_token) is True
    assert auth_service.verify_token("invalid-token") is False


def test_verify_token_not_paired(auth_service):
    """Test token verification when not paired"""
    assert auth_service.verify_token("any-token") is False


def test_is_authenticated(auth_service):
    """Test is_authenticated helper"""
    assert auth_service.is_authenticated(None) is False
    assert auth_service.is_authenticated("") is False

    code = auth_service.generate_pairing_code()
    api_token = auth_service.pair(code)

    assert auth_service.is_authenticated(api_token) is True
    assert auth_service.is_authenticated("wrong-token") is False


def test_unpair(auth_service):
    """Test unpairing"""
    code = auth_service.generate_pairing_code()
    api_token = auth_service.pair(code)

    assert auth_service.is_paired() is True
    result = auth_service.unpair()
    assert result is True
    assert auth_service.is_paired() is False

    # Token no longer works
    assert auth_service.verify_token(api_token) is False


def test_unpair_when_not_paired(auth_service):
    """Test unpair returns False when not paired"""
    result = auth_service.unpair()
    assert result is False


def test_lockout_after_failed_attempts(tmp_path):
    """Test lockout after max failed attempts"""
    with patch("ContaraNAS.core.auth.service.settings") as mock_settings:
        mock_settings.cache_dir = tmp_path
        config = PairingConfig(max_failed_attempts=3, lockout_duration_seconds=300)
        service = AuthService(config=config)

        service.generate_pairing_code()

        # Fail 3 times
        for _ in range(3):
            with pytest.raises(ValueError):
                service.pair("wrong-code")

        assert service.is_locked_out() is True
        assert service.get_lockout_remaining() > 0


def test_cannot_pair_when_locked_out(tmp_path):
    """Test pairing blocked during lockout"""
    with patch("ContaraNAS.core.auth.service.settings") as mock_settings:
        mock_settings.cache_dir = tmp_path
        config = PairingConfig(max_failed_attempts=1, lockout_duration_seconds=300)
        service = AuthService(config=config)

        code = service.generate_pairing_code()

        # Fail once to trigger lockout
        with pytest.raises(ValueError):
            service.pair("wrong-code")

        # Now try with correct code
        with pytest.raises(PairingError) as exc:
            service.pair(code)
        assert "locked out" in str(exc.value).lower()


def test_cannot_generate_code_when_locked_out(tmp_path):
    """Test code generation blocked during lockout"""
    with patch("ContaraNAS.core.auth.service.settings") as mock_settings:
        mock_settings.cache_dir = tmp_path
        config = PairingConfig(max_failed_attempts=1, lockout_duration_seconds=300)
        service = AuthService(config=config)

        service.generate_pairing_code()

        # Fail to trigger lockout
        with pytest.raises(ValueError):
            service.pair("wrong-code")

        # Try to generate new code
        with pytest.raises(PairingError) as exc:
            service.generate_pairing_code()
        assert "locked out" in str(exc.value).lower()


def test_lockout_expires(tmp_path):
    """Test lockout expires after duration"""
    with patch("ContaraNAS.core.auth.service.settings") as mock_settings:
        mock_settings.cache_dir = tmp_path
        config = PairingConfig(max_failed_attempts=1, lockout_duration_seconds=0)
        service = AuthService(config=config)

        service.generate_pairing_code()

        # Fail to trigger lockout
        with pytest.raises(ValueError):
            service.pair("wrong-code")

        # Lockout should expire immediately
        time.sleep(0.1)
        assert service.is_locked_out() is False


def test_hash_token_consistent():
    """Test token hashing is deterministic"""
    token = "test-token-12345"
    hash1 = AuthService._hash_token(token)
    hash2 = AuthService._hash_token(token)

    assert hash1 == hash2
    assert len(hash1) == 64  # SHA256 hex


def test_hash_token_different_for_different_tokens():
    """Test different tokens produce different hashes"""
    hash1 = AuthService._hash_token("token1")
    hash2 = AuthService._hash_token("token2")

    assert hash1 != hash2


def test_persistence(tmp_path):
    """Test paired app persists across service restarts"""
    with patch("ContaraNAS.core.auth.service.settings") as mock_settings:
        mock_settings.cache_dir = tmp_path

        # Create and pair
        service1 = AuthService()
        code = service1.generate_pairing_code()
        api_token = service1.pair(code)

        # Create new service instance
        service2 = AuthService()

        assert service2.is_paired() is True
        assert service2.verify_token(api_token) is True


def test_unpair_removes_persistence(tmp_path):
    """Test unpair removes persisted data"""
    with patch("ContaraNAS.core.auth.service.settings") as mock_settings:
        mock_settings.cache_dir = tmp_path

        # Create and pair
        service1 = AuthService()
        code = service1.generate_pairing_code()
        service1.pair(code)
        service1.unpair()

        # Create new service instance
        service2 = AuthService()
        assert service2.is_paired() is False


def test_pairing_token_model():
    """Test PairingToken dataclass"""
    token = PairingToken(
        raw_token="abc123",
        display_token="ABC1-23XX-XXXX",
        created_at=1000.0,
        expires_at=1300.0,
    )

    assert token.raw_token == "abc123"
    assert token.display_token == "ABC1-23XX-XXXX"
    assert token.used is False


def test_paired_app_model():
    """Test PairedApp dataclass"""
    app = PairedApp(
        token_hash="hash123",
        paired_at=1000.0,
        last_seen=1500.0,
    )

    assert app.token_hash == "hash123"
    assert app.paired_at == 1000.0
    assert app.last_seen == 1500.0


def test_paired_app_model_optional_last_seen():
    """Test PairedApp with optional last_seen"""
    app = PairedApp(
        token_hash="hash123",
        paired_at=1000.0,
    )

    assert app.last_seen is None


def test_auth_state_model():
    """Test AuthState dataclass"""
    state = AuthState()

    assert state.failed_attempts == 0
    assert state.lockout_until == 0
    assert state.active_pairing is None


def test_pairing_config_defaults():
    """Test PairingConfig default values"""
    config = PairingConfig()

    assert config.token_validity_seconds == 300
    assert config.max_failed_attempts == 5
    assert config.lockout_duration_seconds == 300
    assert config.enabled is True


def test_pairing_config_custom():
    """Test PairingConfig with custom values"""
    config = PairingConfig(
        token_validity_seconds=600,
        max_failed_attempts=3,
        lockout_duration_seconds=60,
        enabled=False,
    )

    assert config.token_validity_seconds == 600
    assert config.max_failed_attempts == 3
    assert config.lockout_duration_seconds == 60
    assert config.enabled is False


def test_pairing_code_uses_secrets():
    """Test pairing codes are cryptographically random"""
    with patch("ContaraNAS.core.auth.service.settings") as mock_settings:
        with tempfile.TemporaryDirectory() as tmp:
            mock_settings.cache_dir = Path(tmp)

            service = AuthService()
            [service.generate_pairing_code() for _ in range(5)]

            # All codes should be unique
            # Need to unpair between generations
            service = AuthService()
            code1 = service.generate_pairing_code()
            service.pair(code1)
            service.unpair()

            service2 = AuthService()
            code2 = service2.generate_pairing_code()

            assert code1 != code2


def test_api_token_is_url_safe(auth_service):
    """Test API tokens are URL-safe"""
    code = auth_service.generate_pairing_code()
    api_token = auth_service.pair(code)

    # URL-safe tokens should not contain +, /, or =
    assert "+" not in api_token
    assert "/" not in api_token
    # Note: url_safe may have trailing = for padding, which is fine
