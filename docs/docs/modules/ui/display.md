# Display Components

Display components show information to users without accepting input.

## Text

Renders text content with optional styling variants.

```python
from ContaraNAS.core.ui import Text

# Default body text
Text(content="This is regular body text.")

# Secondary (muted) text
Text(content="Additional information", variant="secondary")

# Muted text (even lighter)
Text(content="Timestamp: 2 hours ago", variant="muted")

# Code/monospace text
Text(content="npm install contaranas", variant="code")
```

### Props

| Prop      | Type                                               | Default  | Description         |
|-----------|----------------------------------------------------|----------|---------------------|
| `content` | `str`                                              | Required | The text to display |
| `variant` | `"body"` \| `"secondary"` \| `"muted"` \| `"code"` | `"body"` | Visual style        |

### Variants

| Variant       | Use Case                             |
|---------------|--------------------------------------|
| `"body"`      | Primary content, normal text         |
| `"secondary"` | Supporting information, descriptions |
| `"muted"`     | Timestamps, metadata, hints          |
| `"code"`      | Code snippets, paths, commands       |

### Examples

```python
from ContaraNAS.core.ui import Stack, Text

description = Stack(
    direction="vertical",
    gap="2",
    children=[
        Text(content="Steam Library", variant="body"),
        Text(content="150 games installed across 3 libraries", variant="secondary"),
        Text(content="Last scanned: 5 minutes ago", variant="muted"),
    ],
)
```

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

| Prop    | Type                                                   | Default     | Description                  |
|---------|--------------------------------------------------------|-------------|------------------------------|
| `label` | `str`                                                  | Required    | Description of the statistic |
| `value` | `str \| int \| float`                                  | Required    | The statistic value          |
| `icon`  | `str \| None`                                          | `None`      | Lucide icon name             |
| `color` | `"default"` \| `"success"` \| `"warning"` \| `"error"` | `"default"` | Color theme                  |
| `trend` | `tuple[Literal["up", "down"], str] \| None`            | `None`      | Trend indicator              |

### Color Usage

Use colors semantically:

```python
# Default - neutral information
StatCard(label="Total", value=1234)

# Success - positive metrics
StatCard(label="Uptime", value="99.9%", color="success")

# Warning - needs attention
StatCard(label="Disk Usage", value="85%", color="warning")

# Error - critical issues
StatCard(label="Errors", value=12, color="error")
```

### Trend Indicators

Show whether a value is increasing or decreasing:

```python
# Value increased by 12%
StatCard(label="Users", value=1234, trend=("up", "+12%"))

# Value decreased by 5%
StatCard(label="Errors", value=8, trend=("down", "-5%"), color="success")
```

---

## Progress

A progress bar showing completion percentage.

```python
from ContaraNAS.core.ui import Progress

# Basic progress
Progress(value=75, max=100)

# With label
Progress(value=75, max=100, label="75%")

# With label and sublabel
Progress(
    value=750,
    max=1000,
    label="750 MB / 1 GB",
    sublabel="Downloading..."
)

# Colored progress
Progress(value=90, max=100, label="90%", color="warning")
```

### Props

| Prop       | Type                                                   | Default     | Description                         |
|------------|--------------------------------------------------------|-------------|-------------------------------------|
| `value`    | `int \| float`                                         | Required    | Current value                       |
| `max`      | `int \| float`                                         | `100`       | Maximum value                       |
| `label`    | `str \| None`                                          | `None`      | Primary label (e.g., percentage)    |
| `sublabel` | `str \| None`                                          | `None`      | Secondary label (e.g., status text) |
| `color`    | `"default"` \| `"success"` \| `"warning"` \| `"error"` | `"default"` | Bar color                           |

### Color Thresholds

A common pattern is to change color based on value:

```python
def get_progress_color(percent: float) -> str:
    if percent >= 90:
        return "error"
    elif percent >= 75:
        return "warning"
    else:
        return "default"

usage_percent = (used / total) * 100
Progress(
    value=usage_percent,
    max=100,
    label=f"{usage_percent:.0f}%",
    color=get_progress_color(usage_percent),
)
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

| Prop      | Type                                                                              | Default     | Description   |
|-----------|-----------------------------------------------------------------------------------|-------------|---------------|
| `text`    | `str`                                                                             | Required    | Badge text    |
| `variant` | `"default"` \| `"primary"` \| `"success"` \| `"warning"` \| `"error"` \| `"info"` | `"default"` | Color variant |

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

table = Table(
    columns=[
        TableColumn(key="name", label="Name"),
        TableColumn(key="size", label="Size", align="right"),
        TableColumn(key="status", label="Status"),
    ],
    data=[
        {"name": "Game A", "size": "50 GB", "status": "Installed"},
        {"name": "Game B", "size": "25 GB", "status": "Updating"},
        {"name": "Game C", "size": "100 GB", "status": "Installed"},
    ],
)
```

### Table Props

| Prop            | Type                   | Default     | Description                |
|-----------------|------------------------|-------------|----------------------------|
| `columns`       | `list[TableColumn]`    | Required    | Column definitions         |
| `data`          | `list[dict[str, Any]]` | Required    | Row data                   |
| `empty_message` | `str`                  | `"No data"` | Message when data is empty |

### TableColumn Props

| Prop    | Type                                | Default  | Description                      |
|---------|-------------------------------------|----------|----------------------------------|
| `key`   | `str`                               | Required | Key in data dict                 |
| `label` | `str`                               | Required | Column header text               |
| `width` | `str \| None`                       | `None`   | CSS width (e.g., "100px", "20%") |
| `align` | `"left"` \| `"center"` \| `"right"` | `"left"` | Text alignment                   |

### Examples

**File listing:**

```python
Table(
    columns=[
        TableColumn(key="name", label="Name"),
        TableColumn(key="size", label="Size", width="100px", align="right"),
        TableColumn(key="modified", label="Modified", width="150px"),
    ],
    data=[
        {"name": "document.pdf", "size": "2.5 MB", "modified": "2024-01-15"},
        {"name": "image.png", "size": "500 KB", "modified": "2024-01-14"},
    ],
    empty_message="No files found",
)
```

**Dynamic data from state:**

```python
table = Table(
    columns=[
        TableColumn(key="name", label="Game"),
        TableColumn(key="size", label="Size", align="right"),
    ],
    data=[
        {"name": game.name, "size": format_size(game.size)}
        for game in state.games[:10]  # Show first 10
    ],
    empty_message="No games found",
)
```

### Empty State

The `empty_message` is shown when `data` is an empty list:

```python
Table(
    columns=[...],
    data=[],  # Empty
    empty_message="No items to display. Add some items to get started.",
)
```

---

## Combining Display Components

Display components work together to create rich interfaces:

```python
from ContaraNAS.core.ui import Stack, Text, Progress, Badge, StatCard, Grid

status_section = Stack(
    direction="vertical",
    gap="4",
    children=[
        # Header with badge
        Stack(
            direction="horizontal",
            justify="between",
            align="center",
            children=[
                Text(content="Download Progress"),
                Badge(text="Active", variant="success"),
            ],
        ),

        # Progress bar
        Progress(
            value=65,
            max=100,
            label="65%",
            sublabel="game_installer.exe (650 MB / 1 GB)",
        ),

        # Stats grid
        Grid(
            columns=3,
            gap="3",
            children=[
                StatCard(label="Speed", value="12.5 MB/s"),
                StatCard(label="ETA", value="5 min"),
                StatCard(label="Queue", value=3),
            ],
        ),

        # Status text
        Text(
            content="2 downloads queued after this one",
            variant="secondary"
        ),
    ],
)
```
