# Card Components

Card components are container elements that group related content.

## Card

A general-purpose container with optional icon, title, and footer.

```python
from ContaraNAS.core.ui import Card, Text, Button, Stack

card = Card(
    icon="ChartBar",
    title="Analytics",
    children=[
        Text(content="View your usage statistics and trends."),
        Text(content="Updated daily.", variant="secondary"),
    ],
    footer=[
        Button(label="View Details", on_click=self.view_details),
    ],
)
```

### Props

| Prop       | Type                        | Default | Description                           |
|------------|-----------------------------|---------|---------------------------------------|
| `icon`     | `str` or `None`             | `None`  | Lucide icon name for the header       |
| `title`    | `str` or `None`             | `None`  | Card title text                       |
| `children` | `list[Component]`           | `[]`    | Main content components               |
| `footer`   | `list[Component]` or `None` | `None`  | Footer components (typically buttons) |

### Examples

**Simple Card:**

```python
Card(
    title="Welcome",
    children=[
        Text(content="Get started by enabling a module."),
    ],
)
```

**Card with Icon:**

```python
Card(
    icon="Settings",
    title="Settings",
    children=[
        Text(content="Configure your preferences."),
    ],
)
```

**Card with Footer:**

```python
Card(
    title="Confirmation",
    children=[
        Text(content="Are you sure you want to delete this item?"),
    ],
    footer=[
        Button(label="Cancel", variant="secondary", on_click=self.cancel),
        Button(label="Delete", variant="danger", on_click=self.delete),
    ],
)
```

---

## Tile

A specialized card designed for module tiles on the dashboard. Tiles have a consistent structure: icon, title, optional
badge, stats, optional content, and actions.

```python
from ContaraNAS.core.ui import Tile, Stat, Badge, Button

tile = Tile(
    icon="Gamepad2",
    title="Steam",
    badge=Badge(text="Active", variant="success"),
    stats=[
        Stat(label="Games", value=150),
        Stat(label="Size", value="2.3 TB"),
        Stat(label="Libraries", value=3),
    ],
    actions=[
        Button(label="Refresh", on_click=self.refresh),
        Button(label="Details", variant="secondary", on_click=self.open_details),
    ],
)
```

### Props

| Prop      | Type                        | Default  | Description                    |
|-----------|-----------------------------|----------|--------------------------------|
| `icon`    | `str`                       | Required | Lucide icon name for the tile  |
| `title`   | `str`                       | Required | Module display name            |
| `colspan` | `1`, `2`, `3`               | `1`      | Number of grid columns to span |
| `rowspan` | `1`, `2`, `3`               | `1`      | Number of grid rows to span    |
| `badge`   | `Badge` or `None`           | `None`   | Status badge next to title     |
| `stats`   | `list[Stat]`                | `[]`     | Key metrics to display         |
| `content` | `list[Component]` or `None` | `None`   | Additional content below stats |
| `actions` | `list[Component]`           | `[]`     | Action buttons                 |

### Spanning

Use `colspan` and `rowspan` to control tile size on the dashboard grid:

```python
# Normal size (1x1)
Tile(icon="Package", title="My Module")

# Double width (2 columns)
Tile(icon="Activity", title="System Monitor", colspan=2)

# Double height (2 rows)
Tile(icon="ChartBar", title="Analytics", rowspan=2)

# Large tile (2x2)
Tile(icon="Server", title="Dashboard", colspan=2, rowspan=2)
```

### Using with get_tile()

The `Tile` component is returned from your module's `get_tile()` method:

```python
class MyModule(Module):
    def get_tile(self) -> Tile:
        state = self._typed_state
        if not state:
            return Tile(icon="Package", title="My Module", stats=[])

        return Tile(
            icon="Package",
            title="My Module",
            stats=[
                Stat(label="Items", value=state.item_count),
                Stat(label="Status", value=state.status),
            ],
            actions=[
                Button(label="Refresh", on_click=self.refresh),
            ],
        )
```

### Badge Variants

Use badges to show module status:

```python
# Module is active/running
badge = Badge(text="Active", variant="success")

# Module has warnings
badge = Badge(text="Warning", variant="warning")

# Module has errors
badge = Badge(text="Error", variant="error")

# Module is syncing/updating
badge = Badge(text="Syncing", variant="info")

# Module is disabled
badge = Badge(text="Disabled", variant="default")
```

### Content Section

The `content` prop allows custom components below the stats:

```python
tile = Tile(
    icon="ClipboardList",
    title="Tasks",
    stats=[
        Stat(label="Pending", value=5),
    ],
    content=[
        Stack(
            direction="vertical",
            gap="1",
            children=[
                Text(content="• Review pull request"),
                Text(content="• Update documentation"),
                Text(content="• Fix login bug"),
            ],
        ),
    ],
    actions=[...],
)
```

---

## Stat

An inline statistic display, typically used inside Tiles.

```python
from ContaraNAS.core.ui import Stat

# Basic stat
stat = Stat(label="Users", value=1234)

# With formatted value
stat = Stat(label="Size", value="2.3 TB")

# With percentage
stat = Stat(label="Usage", value="85%")
```

### Props

| Prop    | Type                  | Default  | Description                  |
|---------|-----------------------|----------|------------------------------|
| `label` | `str`                 | Required | Description of the statistic |
| `value` | `str`, `int`, `float` | Required | The statistic value          |

### Formatting Values

The `value` prop accepts numbers or strings. Format as needed:

```python
# Integer
Stat(label="Count", value=42)

# Float (consider formatting)
Stat(label="Percentage", value=f"{percentage:.1f}%")

# String
Stat(label="Status", value="Healthy")


# Size formatting
def format_size(bytes: int) -> str:
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes < 1024:
            return f"{bytes:.1f} {unit}"
        bytes /= 1024
    return f"{bytes:.1f} PB"


Stat(label="Size", value=format_size(state.size_bytes))
```

### Best Practices for Stats

- **Keep labels short** — "CPU" not "CPU Usage Percentage"
- **Format values appropriately** — "2.3 TB" not "2534023491584 bytes"
- **Limit to 3-4 stats** — Too many stats are hard to scan
- **Order by importance** — Most relevant stat first

For complete module examples, see the [GitHub repository](https://github.com/MihaiStreames/ContaraNAS).
