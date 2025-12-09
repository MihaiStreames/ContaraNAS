import pytest

from ContaraNAS.core.action import (
    ActionDispatcher,
    ActionError,
    ActionRef,
    CloseModal,
    Notify,
    OpenModal,
    Refresh,
    action,
    get_actions,
)
from ContaraNAS.core.module import Module, ModuleState
from ContaraNAS.core.ui import Button, Stat, Tile


class MockState(ModuleState):
    count: int = 0


class MockModule(Module):
    State = MockState

    def __init__(self):
        super().__init__(name="mock")

    async def initialize(self):
        pass

    async def start_monitoring(self):
        pass

    async def stop_monitoring(self):
        pass

    def get_tile(self) -> Tile:
        return Tile(
            icon="box",
            title="Mock Module",
            stats=[
                Stat(
                    label="Count",
                    value=self.typed_state.count if self.typed_state else 0,
                )
            ],
        )

    @action
    async def increment(self):
        """Increment the counter"""
        if self.typed_state:
            self.typed_state.count += 1

    @action
    async def open_settings(self):
        """Open settings modal"""
        return OpenModal(modal_id="settings")

    @action
    async def save_settings(self):
        """Save settings and notify"""
        return [
            Notify(message="Settings saved", variant="success"),
            CloseModal(modal_id="settings"),
        ]

    @action
    async def force_refresh(self):
        """Force UI refresh"""
        return Refresh()

    @action
    async def greet(self, name: str = "World"):
        """Greet with a name"""
        return Notify(message=f"Hello, {name}!")

    @action
    async def failing_action(self):
        """An action that raises an error"""
        raise ValueError("Something went wrong")

    async def not_an_action(self):
        """This is not decorated, should not be callable"""
        pass


def test_action_decorator_marks_method():
    """Test @action decorator sets __action__ attribute"""
    module = MockModule()
    assert hasattr(module.increment, "__action__")
    assert module.increment.__action__ is True


def test_action_decorator_preserves_name():
    """Test @action decorator sets __action_name__"""
    module = MockModule()
    assert module.increment.__action_name__ == "increment"


def test_get_actions_returns_decorated_methods():
    """Test get_actions finds all @action decorated methods"""
    module = MockModule()
    actions = get_actions(module)

    assert "increment" in actions
    assert "open_settings" in actions
    assert "save_settings" in actions
    assert "force_refresh" in actions
    assert "greet" in actions
    assert "failing_action" in actions
    assert "not_an_action" not in actions


def test_get_actions_excludes_private():
    """Test get_actions excludes private methods"""
    module = MockModule()
    actions = get_actions(module)

    assert all(not name.startswith("_") for name in actions)


@pytest.mark.asyncio
async def test_action_auto_commits_state():
    """Test action auto-commits dirty state"""
    module = MockModule()
    assert module.typed_state is not None

    await module.increment()

    assert module.typed_state.count == 1
    assert not module.typed_state.is_dirty


@pytest.mark.asyncio
async def test_dispatcher_register_unregister():
    """Test dispatcher registration"""
    dispatcher = ActionDispatcher()
    module = MockModule()

    dispatcher.register_module(module)
    assert dispatcher.get_module_actions("mock") == list(get_actions(module).keys())

    dispatcher.unregister_module("mock")
    assert dispatcher.get_module_actions("mock") == []


@pytest.mark.asyncio
async def test_dispatcher_dispatch_action():
    """Test dispatcher routes to correct method"""
    dispatcher = ActionDispatcher()
    module = MockModule()
    dispatcher.register_module(module)

    await dispatcher.dispatch("mock", "increment")
    assert module.typed_state.count == 1


@pytest.mark.asyncio
async def test_dispatcher_returns_open_modal():
    """Test dispatcher returns OpenModal result"""
    dispatcher = ActionDispatcher()
    module = MockModule()
    dispatcher.register_module(module)

    results = await dispatcher.dispatch("mock", "open_settings")

    assert len(results) == 1
    assert results[0]["type"] == "open_modal"
    assert results[0]["modal_id"] == "settings"


@pytest.mark.asyncio
async def test_dispatcher_returns_multiple_results():
    """Test dispatcher handles list of results"""
    dispatcher = ActionDispatcher()
    module = MockModule()
    dispatcher.register_module(module)

    results = await dispatcher.dispatch("mock", "save_settings")

    assert len(results) == 2
    assert results[0]["type"] == "notify"
    assert results[0]["message"] == "Settings saved"
    assert results[1]["type"] == "close_modal"


@pytest.mark.asyncio
async def test_dispatcher_with_payload():
    """Test dispatcher passes payload to action"""
    dispatcher = ActionDispatcher()
    module = MockModule()
    dispatcher.register_module(module)

    results = await dispatcher.dispatch("mock", "greet", {"name": "Alice"})

    assert results[0]["message"] == "Hello, Alice!"


@pytest.mark.asyncio
async def test_dispatcher_action_not_found():
    """Test dispatcher raises on unknown action"""
    dispatcher = ActionDispatcher()
    module = MockModule()
    dispatcher.register_module(module)

    with pytest.raises(ActionError) as exc_info:
        await dispatcher.dispatch("mock", "nonexistent")

    assert "not found" in str(exc_info.value)


@pytest.mark.asyncio
async def test_dispatcher_module_not_found():
    """Test dispatcher raises on unknown module"""
    dispatcher = ActionDispatcher()

    with pytest.raises(ActionError) as exc_info:
        await dispatcher.dispatch("unknown", "action")

    assert "not found" in str(exc_info.value)


@pytest.mark.asyncio
async def test_dispatcher_action_error():
    """Test dispatcher wraps exceptions in ActionError when catch_errors=False"""
    dispatcher = ActionDispatcher()
    module = MockModule()
    dispatcher.register_module(module)

    with pytest.raises(ActionError) as exc_info:
        await dispatcher.dispatch("mock", "failing_action", catch_errors=False)

    assert "Something went wrong" in str(exc_info.value)


@pytest.mark.asyncio
async def test_dispatcher_action_error_returns_notify():
    """Test dispatcher returns error Notify when catch_errors=True (default)"""
    dispatcher = ActionDispatcher()
    module = MockModule()
    dispatcher.register_module(module)

    results = await dispatcher.dispatch("mock", "failing_action")

    assert len(results) == 1
    assert results[0]["type"] == "notify"
    assert results[0]["variant"] == "error"
    assert "Something went wrong" in results[0]["message"]


def test_open_modal_result():
    """Test OpenModal serialization"""
    result = OpenModal(modal_id="test-modal")
    data = result.to_dict()

    assert data["type"] == "open_modal"
    assert data["modal_id"] == "test-modal"


def test_close_modal_result():
    """Test CloseModal serialization"""
    result = CloseModal(modal_id="test-modal")
    data = result.to_dict()

    assert data["type"] == "close_modal"
    assert data["modal_id"] == "test-modal"


def test_close_modal_result_no_id():
    """Test CloseModal with no ID closes current modal"""
    result = CloseModal()
    data = result.to_dict()

    assert data["type"] == "close_modal"
    assert "modal_id" not in data  # None values excluded


def test_notify_result():
    """Test Notify serialization"""
    result = Notify(message="Hello", variant="success", title="Greeting")
    data = result.to_dict()

    assert data["type"] == "notify"
    assert data["message"] == "Hello"
    assert data["variant"] == "success"
    assert data["title"] == "Greeting"


def test_notify_result_defaults():
    """Test Notify defaults"""
    result = Notify(message="Test")
    data = result.to_dict()

    assert data["variant"] == "info"
    assert "title" not in data


def test_refresh_result():
    """Test Refresh serialization"""
    result = Refresh()
    data = result.to_dict()

    assert data["type"] == "refresh"


def test_action_ref_creation():
    """Test ActionRef with parameters"""
    module = MockModule()
    ref = ActionRef(module.greet, name="Alice")

    assert ref.__action_name__ == "greet"
    assert ref.__action_params__ == {"name": "Alice"}


def test_action_ref_no_params():
    """Test ActionRef without parameters"""
    module = MockModule()
    ref = ActionRef(module.increment)

    assert ref.__action_name__ == "increment"
    assert ref.__action_params__ is None


def test_action_ref_requires_action_decorator():
    """Test ActionRef raises for non-action methods"""
    module = MockModule()

    with pytest.raises(ValueError) as exc_info:
        ActionRef(module.not_an_action)

    assert "not decorated with @action" in str(exc_info.value)


def test_action_ref_serialization():
    """Test ActionRef serializes correctly via Button"""
    module = MockModule()
    ref = ActionRef(module.greet, name="Bob")

    button = Button(label="Greet Bob", on_click=ref)
    data = button.to_dict()

    assert data["on_click"]["__action__"] == "greet"
    assert data["on_click"]["__params__"] == {"name": "Bob"}
