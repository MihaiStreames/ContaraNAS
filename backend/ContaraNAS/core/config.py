from pathlib import Path
import platform as plat

from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class Settings(BaseSettings):
    """Application settings for ContaraNAS"""

    model_config = SettingsConfigDict(
        env_prefix="CONTARANAS_",
        env_file=".env",
        env_file_encoding="utf-8",
    )

    backend_version: str = "0.1.0"

    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False

    log_level: str = "TRACE"
    log_rotation: str = "10 MB"
    log_retention: str = "1 week"
    log_compression: str = "zip"

    pairing_code_validity_seconds: int = 300
    pairing_max_failed_attempts: int = 5
    pairing_lockout_duration_seconds: int = 300

    cors_origins: list[str] = [
        "http://localhost:1420",
        "http://127.0.0.1:1420",
        "tauri://localhost",
        "https://tauri.localhost",
    ]

    @property
    def log_dir(self) -> Path:
        """Platform-specific log directory"""
        system = plat.system()

        if system == "Linux":
            return Path.home() / ".local" / "share" / "contaranas" / "logs"
        if system == "Windows":
            return Path.home() / "AppData" / "Local" / "ContaraNAS" / "Logs"

        return Path.home() / ".contaranas" / "logs"

    @property
    def cache_dir(self) -> Path:
        """Platform-specific cache directory"""
        system = plat.system()

        if system == "Linux":
            return Path.home() / ".cache" / "contaranas"
        if system == "Windows":
            return Path.home() / "AppData" / "Local" / "ContaraNAS" / "Cache"

        return Path.home() / ".contaranas" / "cache"


settings = Settings()
