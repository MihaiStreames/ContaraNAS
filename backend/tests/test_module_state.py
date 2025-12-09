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
                Stat(
                    label="Counter",
                    value=self.typed_state.counter if self.typed_state else 0,
                )
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


def test_state_commit_triggers_callback():
    module = SampleModule(name="callback_test")
    calls = []

    def capture_callback(m):
        calls.append(m)

    module.set_ui_update_callback(capture_callback)

    module.typed_state.counter = 5
    module.typed_state.commit()

    assert len(calls) == 1
    assert calls[0] is module
    assert module.typed_state.counter == 5


def test_state_with_nested_data():
    """Test state with nested dicts and lists (common in NAS modules)"""

    class NASState(ModuleState):
        volumes: list[dict] = []
        shares: dict[str, dict] = {}
        status: str = "idle"

    state = NASState()
    state.volumes = [
        {"path": "/mnt/data", "size": 1000000000, "used": 500000000},
        {"path": "/mnt/backup", "size": 2000000000, "used": 100000000},
    ]
    state.shares = {
        "media": {"path": "/mnt/data/media", "readonly": False},
        "backup": {"path": "/mnt/backup", "readonly": True},
    }

    data = state.to_dict()
    assert len(data["volumes"]) == 2
    assert data["volumes"][0]["path"] == "/mnt/data"
    assert data["shares"]["media"]["readonly"] is False

    # Test round-trip
    restored = NASState.from_dict(data)
    assert restored.volumes == state.volumes
    assert restored.shares == state.shares


def test_state_with_optional_fields():
    """Test state with optional fields (None values)"""

    class OptionalState(ModuleState):
        error: str | None = None
        last_scan: str | None = None
        active_jobs: int = 0

    state = OptionalState()
    assert state.error is None
    assert state.last_scan is None

    state.error = "Connection failed"
    data = state.to_dict()
    assert data["error"] == "Connection failed"
    assert data["last_scan"] is None

    # Restore with None values
    restored = OptionalState.from_dict({"error": None, "last_scan": None, "active_jobs": 5})
    assert restored.error is None
    assert restored.active_jobs == 5


def test_state_partial_update():
    """Test that partial dict updates work (for persistence)"""
    state = SampleState(counter=10, name="original", items=["a", "b"])

    # Simulate loading partial saved state
    partial = {"counter": 20}
    updated = SampleState.from_dict({**state.to_dict(), **partial})

    assert updated.counter == 20
    assert updated.name == "original"
    assert updated.items == ["a", "b"]


def test_module_render_ui():
    """Test module UI generation"""
    module = SampleModule(name="ui_test")
    module.typed_state.counter = 42

    ui = module.render_ui()
    assert "tile" in ui
    assert ui["tile"]["type"] == "tile"
    assert ui["tile"]["title"] == "Sample"
    assert "modals" in ui


def test_state_history_tracking():
    """Test state suitable for history graphs (like sys_monitor)"""

    class HistoryState(ModuleState):
        cpu_history: list[float] = []
        max_history: int = 60

    state = HistoryState()

    # Simulate adding readings
    for i in range(70):
        state.cpu_history.append(float(i % 100))
        if len(state.cpu_history) > state.max_history:
            state.cpu_history = state.cpu_history[-state.max_history :]

    assert len(state.cpu_history) == 60
    assert state.cpu_history[0] == 10.0  # First kept value
    assert state.cpu_history[-1] == 69.0  # Last value
