class ContaraNASError(Exception):
    """Base exception for ContaraNAS application."""


class ModuleError(ContaraNASError):
    """Base exception for module-related errors"""

    def __init__(self, module_name: str, reason: str):
        self.module_name = module_name
        self.reason = reason
        super().__init__(f"Module '{module_name}' error: {reason}")


class ModuleInitializationError(ModuleError):
    """Raised when a module fails to initialize"""

    def __init__(self, module_name: str, reason: str):
        super().__init__(module_name, reason)
        # Override the message for initialization errors
        Exception.__init__(self, f"Failed to initialize module '{module_name}': {reason}")


class ServiceError(ContaraNASError):
    """Base exception for service-related errors"""


class SteamError(ServiceError):
    """Steam-specific errors"""


class SteamNotFoundError(SteamError):
    """Raised when Steam installation is not found"""
