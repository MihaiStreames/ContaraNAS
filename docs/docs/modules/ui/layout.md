# Layout Components

Layout components control how other components are arranged on screen.

## Stack

A flex container that arranges children in a row or column.

```python
from ContaraNAS.core.ui import Stack, Text, Button

# Vertical stack (default)
vertical = Stack(
    direction="vertical",
    gap="4",
    children=[
        Text(content="First"),
        Text(content="Second"),
        Text(content="Third"),
    ],
)

# Horizontal stack
horizontal = Stack(
    direction="horizontal",
    gap="2",
    align="center",
    children=[
        Button(label="Save"),
        Button(label="Cancel", variant="secondary"),
    ],
)
```

### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `direction` | `"horizontal"` \| `"vertical"` | `"vertical"` | Main axis direction |
| `gap` | `"0"` \| `"1"` \| `"2"` \| `"3"` \| `"4"` \| `"5"` \| `"6"` \| `"8"` | `"4"` | Space between children |
| `align` | `"start"` \| `"center"` \| `"end"` \| `"stretch"` | `"stretch"` | Cross-axis alignment |
| `justify` | `"start"` \| `"center"` \| `"end"` \| `"between"` \| `"around"` | `"start"` | Main-axis alignment |
| `children` | `list[Component]` | `[]` | Child components |

### Gap Scale

The gap values correspond to a spacing scale:

| Value | Approximate Size |
|-------|------------------|
| `"0"` | 0px |
| `"1"` | 4px |
| `"2"` | 8px |
| `"3"` | 12px |
| `"4"` | 16px |
| `"5"` | 20px |
| `"6"` | 24px |
| `"8"` | 32px |

### Alignment Examples

```python
# Center children both axes
centered = Stack(
    direction="vertical",
    align="center",
    justify="center",
    children=[...],
)

# Space children evenly
spaced = Stack(
    direction="horizontal",
    justify="between",
    children=[...],
)

# Align children to end
end_aligned = Stack(
    direction="horizontal",
    justify="end",
    gap="2",
    children=[...],
)
```

### Nesting Stacks

Stacks can be nested to create complex layouts:

```python
layout = Stack(
    direction="vertical",
    gap="4",
    children=[
        # Header row
        Stack(
            direction="horizontal",
            justify="between",
            align="center",
            children=[
                Text(content="Title", variant="body"),
                Badge(text="New", variant="primary"),
            ],
        ),
        # Content
        Text(content="Description goes here...", variant="secondary"),
        # Footer row
        Stack(
            direction="horizontal",
            gap="2",
            justify="end",
            children=[
                Button(label="Cancel", variant="secondary"),
                Button(label="Save", variant="primary"),
            ],
        ),
    ],
)
```

---

## Grid

A CSS Grid container for two-dimensional layouts.

```python
from ContaraNAS.core.ui import Grid, StatCard

# Simple 2-column grid
grid = Grid(
    columns=2,
    gap="4",
    children=[
        StatCard(label="CPU", value="45%"),
        StatCard(label="Memory", value="8.2 GB"),
        StatCard(label="Disk", value="234 GB"),
        StatCard(label="Network", value="1.2 MB/s"),
    ],
)

# 3-column grid
grid_3col = Grid(
    columns=3,
    gap="3",
    children=[...],
)
```

### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `columns` | `int` \| `str` | `2` | Number of columns or CSS grid-template-columns |
| `gap` | `"0"` \| `"1"` \| `"2"` \| `"3"` \| `"4"` \| `"5"` \| `"6"` \| `"8"` | `"4"` | Space between grid items |
| `children` | `list[Component]` | `[]` | Child components |

### Column Options

The `columns` prop accepts either a number or a CSS grid template string:

```python
# Simple: 2 equal columns
Grid(columns=2, children=[...])

# Simple: 4 equal columns
Grid(columns=4, children=[...])

# Advanced: custom template
Grid(columns="1fr 2fr", children=[...])  # Second column is 2x wider
Grid(columns="200px 1fr", children=[...])  # Fixed + flexible
```

### Use Cases

**Stats Dashboard:**

```python
stats_grid = Grid(
    columns=4,
    gap="4",
    children=[
        StatCard(label="Users", value=1234, icon="users"),
        StatCard(label="Sessions", value=567, icon="activity"),
        StatCard(label="Errors", value=3, icon="alert-triangle", color="error"),
        StatCard(label="Uptime", value="99.9%", icon="check-circle", color="success"),
    ],
)
```

**Card Grid:**

```python
card_grid = Grid(
    columns=3,
    gap="4",
    children=[
        Card(title="Card 1", children=[...]),
        Card(title="Card 2", children=[...]),
        Card(title="Card 3", children=[...]),
    ],
)
```

---

## Combining Layout Components

Use Stack and Grid together for complex layouts:

```python
page_layout = Stack(
    direction="vertical",
    gap="6",
    children=[
        # Header
        Stack(
            direction="horizontal",
            justify="between",
            align="center",
            children=[
                Text(content="Dashboard"),
                Button(label="Refresh", on_click=self.refresh),
            ],
        ),

        # Stats grid
        Grid(
            columns=4,
            gap="4",
            children=[
                StatCard(label="Stat 1", value=100),
                StatCard(label="Stat 2", value=200),
                StatCard(label="Stat 3", value=300),
                StatCard(label="Stat 4", value=400),
            ],
        ),

        # Content area
        Stack(
            direction="horizontal",
            gap="4",
            children=[
                Card(title="Left Panel", children=[...]),
                Card(title="Right Panel", children=[...]),
            ],
        ),
    ],
)
```

## Best Practices

### Do

- Use `Stack` for one-dimensional layouts (rows or columns)
- Use `Grid` for two-dimensional layouts (multiple rows and columns)
- Keep gap values consistent within a section
- Use semantic alignment (`justify="between"` for header bars)

### Don't

- Don't over-nest layouts (3+ levels deep is usually too much)
- Don't mix different gap scales without reason
- Don't use Grid for simple row/column layouts (use Stack)
