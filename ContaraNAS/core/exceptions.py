class ContaraNASError(Exception):
    """Base exception for ContaraNAS application."""

    pass


class ModuleError(ContaraNASError):
    """Base exception for module-related errors"""

    pass


class ModuleInitializationError(ModuleError):
    """Raised when a module fails to initialize"""

    def __init__(self, module_name: str, reason: str):
        self.module_name = module_name
        self.reason = reason
        super().__init__(f"Failed to initialize module '{module_name}': {reason}")


class ServiceError(ContaraNASError):
    """Base exception for service-related errors"""

    pass


class SteamError(ServiceError):
    """Steam-specific errors"""

    pass


class SteamNotFoundError(SteamError):
    """Raised when Steam installation is not found"""

    pass
