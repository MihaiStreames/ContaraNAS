from ContaraNAS.core.ui import (
    Alert,
    Badge,
    Button,
    Card,
    Checkbox,
    Component,
    Grid,
    Input,
    LineChart,
    Modal,
    Progress,
    SegmentedProgress,
    SegmentedProgressSegment,
    Select,
    SelectOption,
    Spinner,
    Stack,
    Stat,
    StatCard,
    Tab,
    Table,
    TableColumn,
    Tabs,
    Text,
    Tile,
    Toggle,
)


def test_component_base():
    """Test that Component base class works"""

    class TestComponent(Component):
        _type = "test"
        value: str

    comp = TestComponent(value="hello")
    data = comp.to_dict()

    assert data["type"] == "test"
    assert data["value"] == "hello"


def test_stack_defaults():
    stack = Stack()
    data = stack.to_dict()

    assert data["type"] == "stack"
    assert data["direction"] == "vertical"
    assert data["gap"] == "4"
    assert data["align"] == "stretch"
    assert data["justify"] == "start"
    assert data["children"] == []


def test_stack_with_children():
    stack = Stack(
        direction="horizontal",
        gap="2",
        children=[Text(content="Hello"), Text(content="World")],
    )
    data = stack.to_dict()

    assert data["direction"] == "horizontal"
    assert len(data["children"]) == 2
    assert data["children"][0]["type"] == "text"
    assert data["children"][0]["content"] == "Hello"


def test_grid():
    grid = Grid(columns=3, gap="4")
    data = grid.to_dict()

    assert data["type"] == "grid"
    assert data["columns"] == 3


def test_card():
    card = Card(icon="gamepad", title="Steam", children=[Text(content="Description")])
    data = card.to_dict()

    assert data["type"] == "card"
    assert data["icon"] == "gamepad"
    assert data["title"] == "Steam"
    assert len(data["children"]) == 1


def test_tile():
    tile = Tile(
        icon="gamepad",
        title="Steam",
        badge=Badge(text="Running", variant="success"),
        stats=[Stat(label="Games", value=127), Stat(label="Size", value="1.2 TB")],
        actions=[Button(label="View Games", variant="ghost", size="sm")],
    )
    data = tile.to_dict()

    assert data["type"] == "tile"
    assert data["icon"] == "gamepad"
    assert data["badge"]["type"] == "badge"
    assert data["badge"]["text"] == "Running"
    assert len(data["stats"]) == 2
    assert data["stats"][0]["value"] == 127
    assert len(data["actions"]) == 1


def test_stat():
    stat = Stat(label="Games", value=127)
    data = stat.to_dict()

    assert data["type"] == "stat"
    assert data["label"] == "Games"
    assert data["value"] == 127


def test_stat_card():
    stat = StatCard(label="Uptime", value="98%", icon="check", color="success", trend=("up", "2%"))
    data = stat.to_dict()

    assert data["type"] == "stat_card"
    assert data["color"] == "success"
    assert data["trend"] == ("up", "2%")  # Tuple preserved (JSON will convert to array)


def test_text():
    text = Text(content="Hello", variant="muted")
    data = text.to_dict()

    assert data["type"] == "text"
    assert data["content"] == "Hello"
    assert data["variant"] == "muted"


def test_progress():
    progress = Progress(value=74, max=100, label="Drive Usage", color="warning")
    data = progress.to_dict()

    assert data["type"] == "progress"
    assert data["value"] == 74
    assert data["max"] == 100
    assert data["color"] == "warning"


def test_badge():
    badge = Badge(text="Running", variant="success")
    data = badge.to_dict()

    assert data["type"] == "badge"
    assert data["text"] == "Running"
    assert data["variant"] == "success"


def test_table():
    table = Table(
        columns=[
            TableColumn(key="name", label="Name"),
            TableColumn(key="size", label="Size", align="right"),
        ],
        data=[
            {"name": "Cyberpunk 2077", "size": "65 GB"},
            {"name": "Elden Ring", "size": "44 GB"},
        ],
    )
    data = table.to_dict()

    assert data["type"] == "table"
    assert len(data["columns"]) == 2
    assert data["columns"][1]["align"] == "right"
    assert len(data["data"]) == 2


def test_button():
    button = Button(label="Submit", variant="primary", size="lg", icon="plus")
    data = button.to_dict()

    assert data["type"] == "button"
    assert data["label"] == "Submit"
    assert data["variant"] == "primary"
    assert data["size"] == "lg"
    assert data["icon"] == "plus"


def test_button_with_action():
    def my_action():
        pass

    button = Button(label="Click", on_click=my_action)
    data = button.to_dict()

    assert data["on_click"]["__action__"] == "my_action"


def test_input():
    input_field = Input(
        name="email", label="Email", input_type="email", placeholder="you@example.com"
    )
    data = input_field.to_dict()

    assert data["type"] == "input"
    assert data["name"] == "email"
    assert data["input_type"] == "email"


def test_select():
    select = Select(
        name="theme",
        label="Theme",
        options=[
            SelectOption(value="light", label="Light"),
            SelectOption(value="dark", label="Dark"),
        ],
        value="dark",
    )
    data = select.to_dict()

    assert data["type"] == "select"
    assert len(data["options"]) == 2
    assert data["value"] == "dark"


def test_toggle():
    toggle = Toggle(name="enabled", label="Enable feature", checked=True)
    data = toggle.to_dict()

    assert data["type"] == "toggle"
    assert data["checked"] is True


def test_checkbox():
    checkbox = Checkbox(name="agree", label="I agree", checked=False)
    data = checkbox.to_dict()

    assert data["type"] == "checkbox"
    assert data["checked"] is False


def test_modal():
    modal = Modal(
        id="games-modal",
        title="Installed Games",
        children=[Text(content="List of games...")],
        footer=[Button(label="Cancel", variant="ghost"), Button(label="Confirm")],
    )
    data = modal.to_dict()

    assert data["type"] == "modal"
    assert data["id"] == "games-modal"
    assert len(data["footer"]) == 2


def test_alert():
    alert = Alert(message="Operation completed", variant="success", title="Success")
    data = alert.to_dict()

    assert data["type"] == "alert"
    assert data["variant"] == "success"
    assert data["title"] == "Success"


def test_spinner():
    spinner = Spinner(size="lg", label="Loading...")
    data = spinner.to_dict()

    assert data["type"] == "spinner"
    assert data["size"] == "lg"
    assert data["label"] == "Loading..."


def test_nested_serialization():
    """Test deeply nested component tree serialization"""
    card = Card(
        icon="settings",
        title="Settings",
        children=[
            Stack(
                direction="vertical",
                gap="4",
                children=[
                    Toggle(name="dark_mode", label="Dark Mode", checked=True),
                    Select(
                        name="language",
                        label="Language",
                        options=[SelectOption(value="en", label="English")],
                    ),
                ],
            )
        ],
        footer=[Button(label="Save")],
    )
    data = card.to_dict()

    assert data["type"] == "card"
    assert data["children"][0]["type"] == "stack"
    assert data["children"][0]["children"][0]["type"] == "toggle"
    assert data["children"][0]["children"][1]["type"] == "select"
    assert data["footer"][0]["type"] == "button"


def test_tile_colspan():
    """Test tile with colspan for wider tiles"""
    tile = Tile(
        icon="activity",
        title="System Monitor",
        colspan=2,
        stats=[Stat(label="CPU", value="45%")],
    )
    data = tile.to_dict()

    assert data["type"] == "tile"
    assert data["colspan"] == 2


def test_segmented_progress():
    """Test segmented progress bar"""
    progress = SegmentedProgress(
        segments=[
            SegmentedProgressSegment(value=40, color="primary", label="Games"),
            SegmentedProgressSegment(value=30, color="success", label="Shaders"),
            SegmentedProgressSegment(value=30, color="default", label="Other"),
        ],
        max=100,
        show_legend=True,
    )
    data = progress.to_dict()

    assert data["type"] == "segmented_progress"
    assert len(data["segments"]) == 3
    assert data["segments"][0]["value"] == 40
    assert data["segments"][0]["color"] == "primary"
    assert data["segments"][0]["label"] == "Games"
    assert data["max"] == 100
    assert data["show_legend"] is True


def test_line_chart():
    """Test line chart component"""
    chart = LineChart(
        data=[10, 25, 45, 30, 55, 70],
        max=100,
        min=0,
        height=80,
        color="primary",
        fill=True,
        label="55%",
    )
    data = chart.to_dict()

    assert data["type"] == "line_chart"
    assert data["data"] == [10, 25, 45, 30, 55, 70]
    assert data["max"] == 100
    assert data["min"] == 0
    assert data["height"] == 80
    assert data["color"] == "primary"
    assert data["fill"] is True
    assert data["label"] == "55%"


def test_tabs():
    """Test tabs component"""
    tabs = Tabs(
        tabs=[
            Tab(
                id="cpu",
                label="CPU",
                icon="Cpu",
                children=[Text(content="CPU info")],
            ),
            Tab(
                id="memory",
                label="Memory",
                icon="MemoryStick",
                children=[Text(content="Memory info")],
            ),
        ],
        default_tab="cpu",
        size="sm",
    )
    data = tabs.to_dict()

    assert data["type"] == "tabs"
    assert len(data["tabs"]) == 2
    assert data["tabs"][0]["id"] == "cpu"
    assert data["tabs"][0]["label"] == "CPU"
    assert data["tabs"][0]["icon"] == "Cpu"
    assert data["tabs"][0]["children"][0]["content"] == "CPU info"
    assert data["default_tab"] == "cpu"
    assert data["size"] == "sm"


def test_tab():
    """Test single tab component"""
    tab = Tab(
        id="disk_0",
        label="nvme0n1",
        icon="HardDrive",
        children=[
            Text(content="/home"),
            Progress(value=75, max=100),
        ],
    )
    data = tab.to_dict()

    assert data["type"] == "tab"
    assert data["id"] == "disk_0"
    assert data["label"] == "nvme0n1"
    assert data["icon"] == "HardDrive"
    assert len(data["children"]) == 2
