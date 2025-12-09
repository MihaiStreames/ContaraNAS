# Display Components

Display components show information to users without accepting input.

## Text

Renders text content with optional styling variants.

```python
from ContaraNAS.core.ui import Text

Text(content="This is regular body text.")
Text(content="Additional information", variant="secondary")
Text(content="Timestamp: 2 hours ago", variant="muted")
Text(content="npm install contaranas", variant="code")
Text(content="Large heading", size="xl")
```

### Props

| Prop      | Type                                         | Default  | Description         |
|-----------|----------------------------------------------|----------|---------------------|
| `content` | `str`                                        | Required | The text to display |
| `variant` | `"body"`, `"secondary"`, `"muted"`, `"code"` | `"body"` | Visual style        |
| `size`    | `"sm"`, `"base"`, `"lg"`, `"xl"`             | `"base"` | Font size           |

### Variants

| Variant       | Use Case                             |
|---------------|--------------------------------------|
| `"body"`      | Primary content, normal text         |
| `"secondary"` | Supporting information, descriptions |
| `"muted"`     | Timestamps, metadata, hints          |
| `"code"`      | Code snippets, paths, commands       |

### Sizes

| Size     | Use Case               |
|----------|------------------------|
| `"sm"`   | Small labels, captions |
| `"base"` | Default body text      |
| `"lg"`   | Subheadings, emphasis  |
| `"xl"`   | Headings, large text   |

---

## StatSmall

A compact inline statistic with label and value side by side.

```python
from ContaraNAS.core.ui import StatSmall

StatSmall(label="Games", value=150)
StatSmall(label="Size", value="2.3 TB")
StatSmall(label="Status", value="Active")
```

### Props

| Prop    | Type                  | Default  | Description                  |
|---------|-----------------------|----------|------------------------------|
| `label` | `str`                 | Required | Description of the statistic |
| `value` | `str`, `int`, `float` | Required | The statistic value          |

---

## StatCard

A standalone statistic card, larger than `Stat` and suitable for grids.

```python
from ContaraNAS.core.ui import StatCard, Grid

stats = Grid(
    columns=4,
    gap="4",
    children=[
        StatCard(label="CPU Usage", value="45%", icon="cpu"),
        StatCard(label="Memory", value="8.2 GB", icon="memory-stick"),
        StatCard(label="Disk", value="234 GB", icon="hard-drive"),
        StatCard(label="Uptime", value="5 days", icon="clock", color="success"),
    ],
)
```

### Props

| Prop    | Type                                             | Default     | Description                  |
|---------|--------------------------------------------------|-------------|------------------------------|
| `label` | `str`                                            | Required    | Description of the statistic |
| `value` | `str`, `int`, `float`                            | Required    | The statistic value          |
| `icon`  | `str` or `None`                                  | `None`      | Lucide icon name             |
| `color` | `"default"`, `"success"`, `"warning"`, `"error"` | `"default"` | Color theme                  |
| `trend` | `tuple["up"/"down", str]` or `None`              | `None`      | Trend indicator              |

### Trend Indicators

```python
StatCard(label="Users", value=1234, trend=("up", "+12%"))
StatCard(label="Errors", value=8, trend=("down", "-5%"), color="success")
```

---

## Progress

A progress bar showing completion percentage.

```python
from ContaraNAS.core.ui import Progress

Progress(value=75, max=100)
Progress(value=75, max=100, label="75%")
Progress(value=750, max=1000, label="750 MB / 1 GB", sublabel="Downloading...")
Progress(value=90, max=100, label="90%", color="warning")
Progress(value=50, max=100, size="lg")  # Large size
```

### Props

| Prop       | Type                                             | Default     | Description                         |
|------------|--------------------------------------------------|-------------|-------------------------------------|
| `value`    | `int`, `float`                                   | Required    | Current value                       |
| `max`      | `int`, `float`                                   | `100`       | Maximum value                       |
| `label`    | `str` or `None`                                  | `None`      | Primary label (e.g., percentage)    |
| `sublabel` | `str` or `None`                                  | `None`      | Secondary label (e.g., status text) |
| `color`    | `"default"`, `"success"`, `"warning"`, `"error"` | `"default"` | Bar color                           |
| `size`     | `"sm"`, `"lg"`                                   | `"sm"`      | Bar height                          |

### Color by Threshold

```python
def get_color(percent: float) -> str:
    if percent >= 90: return "error"
    if percent >= 75: return "warning"
    return "default"


Progress(value=usage, max=100, color=get_color(usage))
```

---

## Badge

A small label for status indicators, counts, or categories.

```python
from ContaraNAS.core.ui import Badge

Badge(text="Active", variant="success")
Badge(text="3 new", variant="primary")
Badge(text="Beta", variant="info")
```

### Props

| Prop      | Type                                                                    | Default     | Description   |
|-----------|-------------------------------------------------------------------------|-------------|---------------|
| `text`    | `str`                                                                   | Required    | Badge text    |
| `variant` | `"default"`, `"primary"`, `"success"`, `"warning"`, `"error"`, `"info"` | `"default"` | Color variant |

### Variants

| Variant     | Use Case                    |
|-------------|-----------------------------|
| `"default"` | Neutral, inactive states    |
| `"primary"` | Brand accent, highlights    |
| `"success"` | Positive states, completion |
| `"warning"` | Needs attention, caution    |
| `"error"`   | Errors, critical issues     |
| `"info"`    | Informational, in-progress  |

### Common Patterns

```python
# Status badges
Badge(text="Running", variant="success")
Badge(text="Stopped", variant="default")
Badge(text="Error", variant="error")

# Count badges
Badge(text="5", variant="primary")  # Notification count

# Category badges
Badge(text="Game", variant="info")
Badge(text="Tool", variant="default")

# Version badges
Badge(text="v2.0", variant="primary")
Badge(text="Beta", variant="warning")
```

---

## Table

Display tabular data with columns and rows.

```python
from ContaraNAS.core.ui import Table, TableColumn

Table(
    columns=[
        TableColumn(key="name", label="Name"),
        TableColumn(key="size", label="Size", align="right"),
        TableColumn(key="status", label="Status"),
    ],
    data=[
        {"name": "Game A", "size": "50 GB", "status": "Installed"},
        {"name": "Game B", "size": "25 GB", "status": "Updating"},
    ],
)

# With sorting enabled
Table(
    columns=[...],
    data=[...],
    sortable=True,
    default_sort_key="name",
    default_sort_desc=False,
)
```

### Table Props

| Prop                | Type                   | Default     | Description                     |
|---------------------|------------------------|-------------|---------------------------------|
| `columns`           | `list[TableColumn]`    | Required    | Column definitions              |
| `data`              | `list[dict[str, Any]]` | Required    | Row data                        |
| `empty_message`     | `str`                  | `"No data"` | Message when data is empty      |
| `sortable`          | `bool`                 | `False`     | Enable column sorting           |
| `default_sort_key`  | `str` or `None`        | `None`      | Column key to sort by initially |
| `default_sort_desc` | `bool`                 | `True`      | Sort descending by default      |

### TableColumn Props

| Prop       | Type                            | Default  | Description                       |
|------------|---------------------------------|----------|-----------------------------------|
| `key`      | `str`                           | Required | Key in data dict                  |
| `label`    | `str`                           | Required | Column header text                |
| `width`    | `str` or `None`                 | `None`   | CSS width (e.g., "100px", "20%")  |
| `align`    | `"left"`, `"center"`, `"right"` | `"left"` | Text alignment                    |
| `render`   | `"text"`, `"image"`             | `"text"` | How to render cell values         |
| `sortable` | `bool`                          | `True`   | Whether this column can be sorted |

### Sorting

Enable sorting with `sortable=True` on the table. Control per-column sorting with `sortable` on each column:

```python
Table(
    columns=[
        TableColumn(key="header", label="", width="60px", render="image", sortable=False),
        TableColumn(key="name", label="Game", sortable=True),
        TableColumn(key="size", label="Size", align="right", sortable=True),
    ],
    data=[...],
    sortable=True,
    default_sort_key="name",
    default_sort_desc=False,
)
```

### Image Columns

Use `render="image"` to display images in table cells:

```python
TableColumn(key="header", label="", width="60px", render="image", sortable=False)
```

---

## SegmentedProgress

A progress bar with multiple colored segments, useful for showing breakdowns (e.g., disk usage by category).

```python
from ContaraNAS.core.ui import SegmentedProgress, SegmentedProgressSegment

# Basic segmented progress
progress = SegmentedProgress(
    segments=[
        SegmentedProgressSegment(value=40, color="primary", label="Games"),
        SegmentedProgressSegment(value=20, color="success", label="Shaders"),
        SegmentedProgressSegment(value=15, color="warning", label="Workshop"),
        SegmentedProgressSegment(value=25, color="default", label="Other"),
    ],
    max=100,
)

# With legend
progress = SegmentedProgress(
    segments=[
        SegmentedProgressSegment(value=450, color="primary", label="Games"),
        SegmentedProgressSegment(value=50, color="success", label="Shaders"),
        SegmentedProgressSegment(value=100, color="warning", label="Workshop"),
    ],
    max=1000,
    show_legend=True,
)
```

### SegmentedProgress Props

| Prop          | Type                             | Default  | Description                     |
|---------------|----------------------------------|----------|---------------------------------|
| `segments`    | `list[SegmentedProgressSegment]` | Required | Segments to display             |
| `max`         | `int`, `float`                   | `100`    | Maximum value (sum of segments) |
| `size`        | `"sm"`, `"lg"`                   | `"sm"`   | Bar height                      |
| `show_legend` | `bool`                           | `False`  | Show segment labels below bar   |

### SegmentedProgressSegment Props

| Prop    | Type            | Default  | Description                      |
|---------|-----------------|----------|----------------------------------|
| `value` | `int`, `float`  | Required | Segment size                     |
| `color` | `str`           | Required | CSS color or semantic color name |
| `label` | `str` or `None` | `None`   | Label for legend/tooltip         |

### Color Options

Use semantic colors (`"primary"`, `"success"`, `"warning"`, `"error"`, `"default"`) or CSS color values (`"#3b82f6"`,
`"rgb(34, 197, 94)"`).

---

## LineChart

A simple line chart for time-series data, rendered as SVG.

```python
from ContaraNAS.core.ui import LineChart

LineChart(data=[10, 25, 45, 30, 55, 70, 65, 80, 75, 90], max=100, min=0)
LineChart(data=cpu_history, color="primary", fill=True, label="45.2%")
```

### Props

| Prop     | Type                                                          | Default     | Description                    |
|----------|---------------------------------------------------------------|-------------|--------------------------------|
| `data`   | `list[float]`                                                 | Required    | Y values (rendered left-right) |
| `max`    | `float`                                                       | `100`       | Maximum Y value                |
| `min`    | `float`                                                       | `0`         | Minimum Y value                |
| `height` | `int`                                                         | `80`        | Chart height in pixels         |
| `color`  | `"default"`, `"primary"`, `"success"`, `"warning"`, `"error"` | `"primary"` | Line/fill color                |
| `fill`   | `bool`                                                        | `True`      | Fill area under line           |
| `label`  | `str` or `None`                                               | `None`      | Current value overlay          |

---

## Image

Display an image with optional sizing and border radius.

```python
from ContaraNAS.core.ui import Image

Image(src="https://example.com/image.png", alt="Description")
Image(src="/path/to/image.jpg", width=200, height=150)
Image(src=game.header_url, border_radius="md")
```

### Props

| Prop            | Type                             | Default  | Description                |
|-----------------|----------------------------------|----------|----------------------------|
| `src`           | `str`                            | Required | Image URL                  |
| `alt`           | `str`                            | `""`     | Alt text for accessibility |
| `width`         | `int` or `None`                  | `None`   | Width in pixels            |
| `height`        | `int` or `None`                  | `None`   | Height in pixels           |
| `border_radius` | `"none"`, `"sm"`, `"md"`, `"lg"` | `"sm"`   | Corner rounding            |
