from pathlib import Path


class Config:
    """Marketplace server configuration"""

    # Paths
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    REGISTRY_FILE = DATA_DIR / "registry.json"
    MODULES_DIR = DATA_DIR / "modules"

    # Server
    HOST = "0.0.0.0"
    PORT = 8001

    # Current marketplace version
    VERSION = "0.1.0"


config = Config()
