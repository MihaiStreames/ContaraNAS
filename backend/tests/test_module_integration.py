from ContaraNAS.core.module import Module, ModuleState
from ContaraNAS.core.ui import Button, Modal, Stat, Text, Tile


class SimpleModule(Module):
    class State(ModuleState):
        counter: int = 0

    async def initialize(self):
        pass

    async def start_monitoring(self):
        pass

    async def stop_monitoring(self):
        pass

    def get_tile(self) -> Tile:
        return Tile(
            icon="box",
            title="Simple",
            stats=[
                Stat(label="Counter", value=self._typed_state.counter if self._typed_state else 0)
            ],
        )


class ModuleWithModals(Module):
    class State(ModuleState):
        count: int = 0

    async def initialize(self):
        pass

    async def start_monitoring(self):
        pass

    async def stop_monitoring(self):
        pass

    def get_tile(self) -> Tile:
        return Tile(
            icon="settings",
            title="With Modals",
            stats=[Stat(label="Count", value=self._typed_state.count if self._typed_state else 0)],
            actions=[Button(label="Open", variant="primary")],
        )

    def get_modals(self) -> list[Modal]:
        return [
            Modal(
                id="settings",
                title="Settings",
                children=[Text(content="Settings content")],
                footer=[Button(label="Close", variant="secondary")],
            ),
            Modal(
                id="confirm",
                title="Confirm",
                children=[Text(content="Are you sure?")],
            ),
        ]


def test_get_tile_returns_component():
    module = SimpleModule(name="tile_test")
    tile = module.get_tile()

    assert isinstance(tile, Tile)
    assert tile.icon == "box"
    assert tile.title == "Simple"


def test_get_modals_default_empty():
    module = SimpleModule(name="no_modals")
    modals = module.get_modals()

    assert modals == []


def test_get_modals_returns_list():
    module = ModuleWithModals(name="with_modals")
    modals = module.get_modals()

    assert len(modals) == 2
    assert modals[0].id == "settings"
    assert modals[1].id == "confirm"


def test_render_tile():
    module = SimpleModule(name="render_tile_test")
    module._typed_state.counter = 42

    tile_dict = module.render_tile()

    assert tile_dict["type"] == "tile"
    assert tile_dict["icon"] == "box"
    assert tile_dict["title"] == "Simple"
    assert tile_dict["stats"][0]["value"] == 42


def test_render_modals():
    module = ModuleWithModals(name="render_modals_test")
    modals = module.render_modals()

    assert len(modals) == 2
    assert modals[0]["type"] == "modal"
    assert modals[0]["id"] == "settings"
    assert modals[1]["id"] == "confirm"


def test_render_ui():
    module = ModuleWithModals(name="render_ui_test")
    ui = module.render_ui()

    assert "tile" in ui
    assert "modals" in ui
    assert ui["tile"]["type"] == "tile"
    assert len(ui["modals"]) == 2


def test_state_commit_triggers_callback():
    module = ModuleWithModals(name="commit_ui_test")
    calls = []

    def capture_callback(m):
        calls.append(m)

    module.set_ui_update_callback(capture_callback)

    module._typed_state.count = 10
    module._typed_state.commit()

    assert len(calls) == 1
    assert calls[0] is module

    # Verify UI can be rendered from the module
    ui = module.render_ui()
    assert ui["tile"]["type"] == "tile"
    assert len(ui["modals"]) == 2
