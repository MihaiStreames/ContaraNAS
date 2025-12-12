class ContaraNASError(Exception):
    """Base exception for the application"""


class ModuleError(ContaraNASError):
    """Module-related errors"""

    def __init__(self, module_name: str, reason: str):
        self._module_name = module_name
        self._reason = reason
        super().__init__(f"Module '{self._module_name}' error: {self._reason}")


class ModuleInitializationError(ModuleError):
    """Raised when a module fails to initialize"""

    def __init__(self, module_name: str, reason: str):
        super().__init__(module_name, reason)
        # Override the message for initialization errors
        Exception.__init__(self, f"Failed to initialize module '{module_name}': {reason}")


class ServiceError(ContaraNASError):
    """Service-related errors"""


class SteamError(ServiceError):
    """Steam-related errors"""


class SteamNotFoundError(SteamError):
    """Raised when Steam installation is not found"""


class ConfigurationError(ContaraNASError):
    """Configuration-related errors"""


class AuthError(ContaraNASError):
    """Authentication errors"""


class PairingError(AuthError):
    """Pairing-related errors"""


class ActionError(ContaraNASError):
    """Raised when an action fails"""

    def __init__(self, action_name: str, message: str):
        self.action_name = action_name
        self.message = message
        super().__init__(f"Action '{action_name}' failed: {message}")
