from enum import Enum


class ModuleCategory(Enum):
    """Categories for organizing modules"""

    MONITORING = "monitoring"
    MEDIA = "media"
    STORAGE = "storage"
    NETWORKING = "networking"
    BACKUP = "backup"
    GAMING = "gaming"
    DOWNLOADERS = "downloaders"
    HOME_AUTOMATION = "home_automation"
    DEVELOPMENT = "development"
    OTHER = "other"
