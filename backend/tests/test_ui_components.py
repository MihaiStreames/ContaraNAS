from ContaraNAS.core.ui import Alert
from ContaraNAS.core.ui import Badge
from ContaraNAS.core.ui import Button
from ContaraNAS.core.ui import Card
from ContaraNAS.core.ui import Checkbox
from ContaraNAS.core.ui import Component
from ContaraNAS.core.ui import Grid
from ContaraNAS.core.ui import Image
from ContaraNAS.core.ui import Input
from ContaraNAS.core.ui import LineChart
from ContaraNAS.core.ui import Modal
from ContaraNAS.core.ui import Progress
from ContaraNAS.core.ui import SegmentedProgress
from ContaraNAS.core.ui import SegmentedProgressSegment
from ContaraNAS.core.ui import Select
from ContaraNAS.core.ui import SelectOption
from ContaraNAS.core.ui import Spinner
from ContaraNAS.core.ui import Stack
from ContaraNAS.core.ui import Stat
from ContaraNAS.core.ui import StatCard
from ContaraNAS.core.ui import StatSmall
from ContaraNAS.core.ui import Tab
from ContaraNAS.core.ui import Table
from ContaraNAS.core.ui import TableColumn
from ContaraNAS.core.ui import Tabs
from ContaraNAS.core.ui import Text
from ContaraNAS.core.ui import Tile
from ContaraNAS.core.ui import Toggle


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


def test_stat_small():
    """Test compact inline stat component"""
    stat = StatSmall(label="Base Speed", value="3.60 GHz")
    data = stat.to_dict()

    assert data["type"] == "stat_small"
    assert data["label"] == "Base Speed"
    assert data["value"] == "3.60 GHz"


def test_stat_small_numeric_value():
    """Test StatSmall with numeric value"""
    stat = StatSmall(label="Cores", value=8)
    data = stat.to_dict()

    assert data["type"] == "stat_small"
    assert data["label"] == "Cores"
    assert data["value"] == 8


def test_text_with_size():
    """Test text component with size variants"""
    text_sm = Text(content="Small", variant="body", size="sm")
    text_xl = Text(content="Extra Large", variant="body", size="xl")

    data_sm = text_sm.to_dict()
    data_xl = text_xl.to_dict()

    assert data_sm["type"] == "text"
    assert data_sm["content"] == "Small"
    assert data_sm["size"] == "sm"

    assert data_xl["size"] == "xl"


def test_text_default_size():
    """Test text component default size is 'base'"""
    text = Text(content="Default")
    data = text.to_dict()

    assert data["size"] == "base"


def test_tile_rowspan():
    """Test tile with rowspan for taller tiles"""
    tile = Tile(
        icon="activity",
        title="System Monitor",
        colspan=2,
        rowspan=2,
        stats=[Stat(label="CPU", value="45%")],
    )
    data = tile.to_dict()

    assert data["type"] == "tile"
    assert data["colspan"] == 2
    assert data["rowspan"] == 2


def test_tile_default_rowspan():
    """Test tile default rowspan is 1"""
    tile = Tile(icon="box", title="Test")
    data = tile.to_dict()

    assert data["rowspan"] == 1


def test_grid_row_height():
    """Test grid with row_height for supporting rowspan"""
    grid = Grid(columns=3, gap="4", row_height="minmax(200px, auto)")
    data = grid.to_dict()

    assert data["type"] == "grid"
    assert data["columns"] == 3
    assert data["row_height"] == "minmax(200px, auto)"


def test_grid_default_row_height():
    """Test grid default row_height is None (excluded from dict)"""
    grid = Grid(columns=2)
    data = grid.to_dict()

    # None values are excluded from serialization
    assert "row_height" not in data or data.get("row_height") is None


def test_image():
    """Test image component"""
    image = Image(
        src="https://example.com/image.png",
        alt="Test image",
        width=200,
        height=150,
        border_radius="md",
    )
    data = image.to_dict()

    assert data["type"] == "image"
    assert data["src"] == "https://example.com/image.png"
    assert data["alt"] == "Test image"
    assert data["width"] == 200
    assert data["height"] == 150
    assert data["border_radius"] == "md"


def test_image_defaults():
    """Test image component default values"""
    image = Image(src="https://example.com/image.png")
    data = image.to_dict()

    assert data["type"] == "image"
    assert data["src"] == "https://example.com/image.png"
    assert data["alt"] == ""
    assert data["border_radius"] == "sm"


def test_stack_on_click():
    """Test stack with on_click handler"""

    def my_handler():
        pass

    stack = Stack(
        direction="horizontal",
        children=[Text(content="Click me")],
        on_click=my_handler,
    )
    data = stack.to_dict()

    assert data["type"] == "stack"
    assert data["on_click"]["__action__"] == "my_handler"


def test_stack_grow():
    """Test stack with grow prop"""
    stack = Stack(direction="horizontal", grow=True, children=[])
    data = stack.to_dict()

    assert data["type"] == "stack"
    assert data["grow"] is True


def test_stack_default_grow():
    """Test stack default grow is False"""
    stack = Stack()
    data = stack.to_dict()

    assert data["grow"] is False


def test_table_sortable():
    """Test table with sorting enabled"""
    table = Table(
        columns=[
            TableColumn(key="name", label="Name"),
            TableColumn(key="size", label="Size", align="right"),
        ],
        data=[{"name": "Game A", "size": "50 GB"}],
        sortable=True,
        default_sort_key="name",
        default_sort_desc=False,
    )
    data = table.to_dict()

    assert data["type"] == "table"
    assert data["sortable"] is True
    assert data["default_sort_key"] == "name"
    assert data["default_sort_desc"] is False


def test_table_sortable_defaults():
    """Test table sorting default values"""
    table = Table(
        columns=[TableColumn(key="name", label="Name")],
        data=[],
    )
    data = table.to_dict()

    assert data["sortable"] is False
    assert data["default_sort_desc"] is True


def test_table_column_render():
    """Test table column with render type"""
    col = TableColumn(key="image", label="", render="image", sortable=False)
    data = col.to_dict()

    assert data["type"] == "table_column"
    assert data["render"] == "image"
    assert data["sortable"] is False


def test_table_column_defaults():
    """Test table column default values"""
    col = TableColumn(key="name", label="Name")
    data = col.to_dict()

    assert data["render"] == "text"
    assert data["sortable"] is True


def test_progress_size():
    """Test progress bar with size"""
    progress = Progress(value=50, max=100, size="lg")
    data = progress.to_dict()

    assert data["type"] == "progress"
    assert data["size"] == "lg"


def test_progress_default_size():
    """Test progress bar default size"""
    progress = Progress(value=50, max=100)
    data = progress.to_dict()

    assert data["size"] == "sm"
