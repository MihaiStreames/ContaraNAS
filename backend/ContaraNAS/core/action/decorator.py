from collections.abc import Callable, Coroutine
from functools import wraps
from typing import Any, ParamSpec, TypeVar


P = ParamSpec("P")
R = TypeVar("R")


def action(func: Callable[P, R]) -> Callable[P, Coroutine[Any, Any, R]]:
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
    setattr(wrapper, "__action__", True)
    setattr(wrapper, "__action_name__", func.__name__)

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
