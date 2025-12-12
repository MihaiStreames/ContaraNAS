from collections.abc import Callable
from collections.abc import Coroutine
from functools import wraps
from typing import Any
from typing import ParamSpec
from typing import TypeVar


P = ParamSpec("P")
R = TypeVar("R")


def action[**P, R](func: Callable[P, R]) -> Callable[P, Coroutine[Any, Any, R]]:
    """Decorator to mark a method as an action callable from frontend"""

    @wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        result = func(*args, **kwargs)

        # Handle async functions
        if hasattr(result, "__await__"):
            result = await result

        # Auto-commit state after action if module has typed state
        if args and hasattr(args[0], "_typed_state"):
            state = args[0]._typed_state
            if state is not None and state.is_dirty:
                state.commit()

        return result

    # Mark as action
    wrapper.__action__ = True
    wrapper.__action_name__ = func.__name__

    return wrapper


def get_actions(obj: Any) -> dict[str, Callable[..., Any]]:
    """Get all action methods from an object"""
    actions: dict[str, Callable[..., Any]] = {}
    for name in dir(obj):
        if name.startswith("_"):
            continue
        try:
            method = getattr(obj, name, None)
        except Exception:
            continue
        if callable(method) and getattr(method, "__action__", False):
            actions[name] = method
    return actions


class ActionRef:
    """
    A reference to an action with parameters.

    Used to create clickable actions that pass parameters to the backend.
    Example: ActionRef(self.open_library, library_path="/home/steam")
    """

    __slots__ = ("__action_name__", "__action_params__")

    def __init__(self, method: Callable[..., Any], **params: Any) -> None:
        action_name = getattr(method, "__action_name__", None)
        if not action_name:
            raise ValueError(f"Method {method} is not decorated with @action")
        self.__action_name__ = action_name
        self.__action_params__ = params if params else None

    def __call__(self) -> None:
        """Dummy callable - actual execution happens via serialization"""
        pass
