import pytest

from ContaraNAS.core.action import ActionDispatcher
from ContaraNAS.core.action import ActionError
from ContaraNAS.core.action import Notify
from ContaraNAS.core.action import action
from ContaraNAS.core.module import Module
from ContaraNAS.core.module import ModuleState
from ContaraNAS.core.ui import Button
from ContaraNAS.core.ui import Stat
from ContaraNAS.core.ui import Tile


class WorkingModule(Module):
    """A module that works correctly"""

    class State(ModuleState):
        counter: int = 0
        last_action: str | None = None

    async def initialize(self):
        pass

    async def start_monitoring(self):
        pass

    async def stop_monitoring(self):
        pass

    def get_tile(self) -> Tile:
        return Tile(
            icon="Box",
            title="Working Module",
            stats=[Stat(label="Counter", value=self._typed_state.counter)],
            actions=[Button(label="Increment", on_click=self.increment)],
        )

    @action
    async def increment(self) -> Notify:
        """Increment counter"""
        self._typed_state.counter += 1
        self._typed_state.last_action = "increment"
        return Notify(message="Incremented!", variant="success")

    @action
    async def failing_action(self) -> Notify:
        """An action that always fails"""
        raise ValueError("This action always fails")


class BrokenTileModule(Module):
    """A module whose get_tile() raises an exception"""

    class State(ModuleState):
        value: int = 0

    async def initialize(self):
        pass

    async def start_monitoring(self):
        pass

    async def stop_monitoring(self):
        pass

    def get_tile(self) -> Tile:
        # Simulate a bug in get_tile()
        raise RuntimeError("Tile rendering crashed!")

    @action
    async def do_something(self) -> Notify:
        return Notify(message="Did something", variant="success")


class BrokenModalModule(Module):
    """A module whose get_modals() raises an exception"""

    async def initialize(self):
        pass

    async def start_monitoring(self):
        pass

    async def stop_monitoring(self):
        pass

    def get_tile(self) -> Tile:
        return Tile(icon="Box", title="Broken Modal Module", stats=[])

    def get_modals(self):
        raise RuntimeError("Modal rendering crashed!")


@pytest.mark.asyncio
async def test_module_enable_disable_lifecycle():
    """Test full module enable/disable cycle"""
    module = WorkingModule(name="lifecycle_test")

    # Initial state
    assert not module.enable_flag
    assert not module.init_flag
    assert module.typed_state.counter == 0

    # Enable
    await module.enable()
    assert module.enable_flag
    assert module.init_flag

    # Disable
    await module.disable()
    assert not module.enable_flag
    assert module.init_flag  # Still initialized


@pytest.mark.asyncio
async def test_module_state_commit_triggers_callback():
    """Test that state commit triggers UI update callback"""
    module = WorkingModule(name="callback_test")
    await module.enable()

    callbacks = []

    def capture_callback(m):
        callbacks.append(m.name)

    module.set_ui_update_callback(capture_callback)

    # Modify state and commit
    module.typed_state.counter = 5
    module.typed_state.commit()

    assert len(callbacks) == 1
    assert callbacks[0] == "callback_test"


@pytest.mark.asyncio
async def test_module_render_ui_after_state_change():
    """Test that UI reflects state changes"""
    module = WorkingModule(name="render_test")
    await module.enable()

    # Initial render
    ui1 = module.render_ui()
    assert ui1["tile"]["stats"][0]["value"] == 0

    # Change state
    module.typed_state.counter = 42
    module.typed_state.commit()

    # Render again
    ui2 = module.render_ui()
    assert ui2["tile"]["stats"][0]["value"] == 42


@pytest.mark.asyncio
async def test_action_dispatch_success():
    """Test successful action dispatch updates state"""
    module = WorkingModule(name="action_test")
    await module.enable()

    dispatcher = ActionDispatcher()
    dispatcher.register_module(module)

    # Dispatch action
    results = await dispatcher.dispatch("action_test", "increment")

    # Verify state changed
    assert module.typed_state.counter == 1
    assert module.typed_state.last_action == "increment"

    # Verify notification returned
    assert len(results) == 1
    assert results[0]["type"] == "notify"
    assert results[0]["variant"] == "success"


@pytest.mark.asyncio
async def test_action_dispatch_with_payload():
    """Test action dispatch passes payload correctly"""

    class PayloadModule(Module):
        class State(ModuleState):
            name: str = ""

        async def initialize(self):
            pass

        async def start_monitoring(self):
            pass

        async def stop_monitoring(self):
            pass

        def get_tile(self) -> Tile:
            return Tile(icon="Box", title="Payload", stats=[])

        @action
        async def set_name(self, name: str) -> Notify:
            self._typed_state.name = name
            return Notify(message=f"Name set to {name}", variant="success")

    module = PayloadModule(name="payload_test")
    await module.enable()

    dispatcher = ActionDispatcher()
    dispatcher.register_module(module)

    results = await dispatcher.dispatch("payload_test", "set_name", {"name": "Alice"})

    assert module.typed_state.name == "Alice"
    assert "Alice" in results[0]["message"]


@pytest.mark.asyncio
async def test_action_triggers_ui_update():
    """Test that action commit triggers UI callback"""
    module = WorkingModule(name="action_ui_test")
    await module.enable()

    callbacks = []
    module.set_ui_update_callback(lambda m: callbacks.append(m.name))

    dispatcher = ActionDispatcher()
    dispatcher.register_module(module)

    await dispatcher.dispatch("action_ui_test", "increment")

    # Action should have triggered commit which triggers callback
    assert "action_ui_test" in callbacks


@pytest.mark.asyncio
async def test_broken_tile_renders_error_tile():
    """Test that broken get_tile() returns error tile instead of crashing"""
    module = BrokenTileModule(name="broken_tile")
    await module.enable()

    # Should not raise
    ui = module.render_ui()

    # Should contain error tile
    tile = ui["tile"]
    assert tile["type"] == "tile"
    assert tile["icon"] == "AlertTriangle"
    assert tile["badge"]["text"] == "Error"
    assert any("crashed" in str(c).lower() for c in tile.get("content", []))


@pytest.mark.asyncio
async def test_broken_modals_returns_empty_list():
    """Test that broken get_modals() returns empty list instead of crashing"""
    module = BrokenModalModule(name="broken_modal")
    await module.enable()

    # Should not raise
    ui = module.render_ui()

    # Tile should work
    assert ui["tile"]["type"] == "tile"

    # Modals should be empty (not crash)
    assert ui["modals"] == []


@pytest.mark.asyncio
async def test_action_error_returns_notify_not_crash():
    """Test that action errors return error notification instead of crashing"""
    module = WorkingModule(name="error_test")
    await module.enable()

    dispatcher = ActionDispatcher()
    dispatcher.register_module(module)

    # With catch_errors=True (default), should return error notify
    results = await dispatcher.dispatch("error_test", "failing_action")

    assert len(results) == 1
    assert results[0]["type"] == "notify"
    assert results[0]["variant"] == "error"
    assert "failed" in results[0]["message"].lower()


@pytest.mark.asyncio
async def test_action_error_raises_when_catch_disabled():
    """Test that action errors raise when catch_errors=False"""
    module = WorkingModule(name="raise_test")
    await module.enable()

    dispatcher = ActionDispatcher()
    dispatcher.register_module(module)

    # With catch_errors=False, should raise ActionError
    with pytest.raises(ActionError) as exc_info:
        await dispatcher.dispatch("raise_test", "failing_action", catch_errors=False)

    assert "always fails" in str(exc_info.value)


@pytest.mark.asyncio
async def test_action_module_not_found():
    """Test that missing module raises ActionError"""
    dispatcher = ActionDispatcher()

    with pytest.raises(ActionError) as exc_info:
        await dispatcher.dispatch("nonexistent", "some_action")

    assert "not found" in str(exc_info.value)


@pytest.mark.asyncio
async def test_action_not_found():
    """Test that missing action raises ActionError"""
    module = WorkingModule(name="missing_action_test")
    await module.enable()

    dispatcher = ActionDispatcher()
    dispatcher.register_module(module)

    with pytest.raises(ActionError) as exc_info:
        await dispatcher.dispatch("missing_action_test", "nonexistent_action")

    assert "not found" in str(exc_info.value)


@pytest.mark.asyncio
async def test_full_flow_enable_action_render():
    """Test complete flow: enable module, dispatch action, verify UI updated"""
    module = WorkingModule(name="full_flow")

    # Track UI updates
    ui_updates = []
    module.set_ui_update_callback(lambda m: ui_updates.append(m.render_ui()))

    # Enable module
    await module.enable()
    assert len(ui_updates) == 1  # Enable triggers UI update

    # Set up dispatcher
    dispatcher = ActionDispatcher()
    dispatcher.register_module(module)

    # Dispatch action
    results = await dispatcher.dispatch("full_flow", "increment")

    # Verify action returned notification
    assert results[0]["type"] == "notify"
    assert results[0]["variant"] == "success"

    # Verify UI was updated (action auto-commits)
    assert len(ui_updates) == 2

    # Verify final UI state
    final_ui = module.render_ui()
    assert final_ui["tile"]["stats"][0]["value"] == 1


@pytest.mark.asyncio
async def test_multiple_modules_independent():
    """Test that multiple modules don't interfere with each other"""
    module1 = WorkingModule(name="module1")
    module2 = WorkingModule(name="module2")

    await module1.enable()
    await module2.enable()

    dispatcher = ActionDispatcher()
    dispatcher.register_module(module1)
    dispatcher.register_module(module2)

    # Dispatch to module1
    await dispatcher.dispatch("module1", "increment")
    await dispatcher.dispatch("module1", "increment")

    # Dispatch to module2
    await dispatcher.dispatch("module2", "increment")

    # Verify independent state
    assert module1.typed_state.counter == 2
    assert module2.typed_state.counter == 1


@pytest.mark.asyncio
async def test_module_error_doesnt_affect_others():
    """Test that one module's error doesn't crash others"""
    working = WorkingModule(name="working")
    broken = BrokenTileModule(name="broken")

    await working.enable()
    await broken.enable()

    # Broken module renders error tile
    broken_ui = broken.render_ui()
    assert broken_ui["tile"]["badge"]["text"] == "Error"

    # Working module still works
    working_ui = working.render_ui()
    assert working_ui["tile"]["title"] == "Working Module"
    assert "Error" not in str(working_ui)
