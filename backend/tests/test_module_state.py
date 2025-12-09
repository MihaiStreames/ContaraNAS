from ContaraNAS.core.event_bus import event_bus
from ContaraNAS.core.module import Module, ModuleState
from ContaraNAS.core.ui import Stat, Tile


class SampleState(ModuleState):
    counter: int = 0
    name: str = "default"
    items: list[str] = []


class SampleModule(Module):
    class State(ModuleState):
        counter: int = 0
        name: str = "default"

    async def initialize(self):
        pass

    async def start_monitoring(self):
        pass

    async def stop_monitoring(self):
        pass

    def get_tile(self) -> Tile:
        return Tile(
            icon="box",
            title="Sample",
            stats=[
                Stat(label="Counter", value=self.typed_state.counter if self.typed_state else 0)
            ],
        )


def test_state_creation():
    state = SampleState()
    assert state.counter == 0
    assert state.name == "default"
    assert state.items == []


def test_dirty_tracking():
    state = SampleState()
    assert not state.is_dirty

    state.counter = 1
    assert state.is_dirty

    state.commit()
    assert not state.is_dirty

    state.name = "changed"
    assert state.is_dirty


def test_serialization():
    state = SampleState(counter=5, name="test", items=["a", "b"])
    data = state.to_dict()

    assert data["counter"] == 5
    assert data["name"] == "test"
    assert data["items"] == ["a", "b"]


def test_deserialization():
    data = {"counter": 10, "name": "restored", "items": ["x"]}
    state = SampleState.from_dict(data)

    assert state.counter == 10
    assert state.name == "restored"
    assert state.items == ["x"]


def test_commit_callback():
    state = SampleState()
    callback_called = False

    def on_commit():
        nonlocal callback_called
        callback_called = True

    state.set_commit_callback(on_commit)
    state.commit()

    assert callback_called


def test_get_changes():
    state = SampleState()
    state.commit()

    state.counter = 5
    state.name = "new"

    changes = state.get_changes()
    assert changes is not None
    assert changes["counter"] == 5
    assert changes["name"] == "new"


def test_module_typed_state():
    module = SampleModule(name="test")

    assert module.typed_state is not None
    assert module.typed_state.counter == 0
    assert module.typed_state.name == "default"

    module.typed_state.counter = 10
    assert module.typed_state.is_dirty


def test_module_without_state():
    class NoStateModule(Module):
        async def initialize(self):
            pass

        async def start_monitoring(self):
            pass

        async def stop_monitoring(self):
            pass

        def get_tile(self) -> Tile:
            return Tile(icon="box", title="No State", stats=[])

    module = NoStateModule(name="nostate")
    assert module.typed_state is None


def test_state_commit_emits_event():
    module = SampleModule(name="event_test")
    events = []

    def capture_event(data):
        events.append(data)

    event_bus.subscribe("module.event_test.state_committed", capture_event)

    module.typed_state.counter = 5
    module.typed_state.commit()

    assert len(events) == 1
    assert events[0]["name"] == "event_test"
    assert events[0]["state"]["counter"] == 5

    event_bus.unsubscribe("module.event_test.state_committed", capture_event)
