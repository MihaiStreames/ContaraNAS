from typing import TYPE_CHECKING, Any

from ContaraNAS.core.exceptions import ActionError
from ContaraNAS.core.utils import get_logger

from .decorator import get_actions
from .results import ActionResult, Notify


if TYPE_CHECKING:
    from ContaraNAS.core.module import Module

logger = get_logger(__name__)


class ActionDispatcher:
    """Routes action calls to module methods"""

    def __init__(self):
        self._modules: dict[str, Module] = {}

    def register_module(self, module: "Module") -> None:
        """Register a module for action dispatching"""
        self._modules[module.name] = module
        logger.debug(f"Registered module {module.name} for actions")

    def unregister_module(self, module_name: str) -> None:
        """Unregister a module"""
        if module_name in self._modules:
            del self._modules[module_name]
            logger.debug(f"Unregistered module {module_name} from actions")

    def get_module_actions(self, module_name: str) -> list[str]:
        """Get list of action names for a module"""
        module = self._modules.get(module_name)
        if module is None:
            return []
        return list(get_actions(module).keys())

    async def dispatch(
        self,
        module_name: str,
        action_name: str,
        payload: dict[str, Any] | None = None,
        catch_errors: bool = True,
    ) -> list[dict[str, Any]]:
        """Dispatch an action to a module method"""
        module = self._modules.get(module_name)
        if module is None:
            raise ActionError(action_name, f"Module '{module_name}' not found")

        actions = get_actions(module)
        action_method = actions.get(action_name)
        if action_method is None:
            raise ActionError(
                action_name,
                f"Action '{action_name}' not found on module '{module_name}'",
            )

        logger.debug(f"Dispatching action {module_name}.{action_name}")

        try:
            result = await action_method(**(payload or {}))
        except Exception as e:
            logger.exception(f"Action {module_name}.{action_name} failed: {e}")
            if catch_errors:
                # Return error as notification instead of crashing
                return self._error_result(action_name, str(e))
            raise ActionError(action_name, str(e)) from e

        return self._process_results(result)

    def _process_results(self, result: Any) -> list[dict[str, Any]]:
        """Process action results into serializable format"""
        if result is None:
            return []

        if isinstance(result, ActionResult):
            return [result.to_dict()]

        if isinstance(result, list):
            return [item.to_dict() for item in result if isinstance(item, ActionResult)]

        return []

    def _error_result(self, action_name: str, error_message: str) -> list[dict[str, Any]]:
        """Create an error notification result"""
        return [
            Notify(
                message=f"Action failed: {error_message}",
                variant="error",
                title=f"{action_name} error",
            ).to_dict()
        ]
