# Layout Components

Layout components control how other components are arranged on screen.

## Stack

A flex container that arranges children in a row or column.

```python
from ContaraNAS.core.ui import Stack, Text, Button

Stack(direction="vertical", gap="4", children=[Text(content="First"), Text(content="Second")])
Stack(direction="horizontal", gap="2", justify="between", children=[...])
Stack(direction="horizontal", on_click=self.open_details, children=[...])  # Clickable
Stack(direction="horizontal", grow=True, children=[...])  # Children fill space
```

### Props

| Prop        | Type                                                    | Default      | Description                             |
|-------------|---------------------------------------------------------|--------------|-----------------------------------------|
| `direction` | `"horizontal"`, `"vertical"`                            | `"vertical"` | Main axis direction                     |
| `gap`       | `"0"`, `"1"`, `"2"`, `"3"`, `"4"`, `"5"`, `"6"`, `"8"`  | `"4"`        | Space between children                  |
| `align`     | `"start"`, `"center"`, `"end"`, `"stretch"`             | `"stretch"`  | Cross-axis alignment                    |
| `justify`   | `"start"`, `"center"`, `"end"`, `"between"`, `"around"` | `"start"`    | Main-axis alignment                     |
| `grow`      | `bool`                                                  | `False`      | Children fill available space (flex: 1) |
| `on_click`  | `Callable` or `None`                                    | `None`       | Makes stack clickable                   |
| `children`  | `list[Component]`                                       | `[]`         | Child components                        |

### Clickable Stack

Use `on_click` to make the entire stack clickable:

```python
Stack(
    direction="horizontal",
    gap="2",
    on_click=self.open_game_details,
    children=[
        Image(src=game.header_url, width=60),
        Text(content=game.name),
    ],
)
```

### Gap Scale

| Value | Size |
|-------|------|
| `"0"` | 0px  |
| `"1"` | 4px  |
| `"2"` | 8px  |
| `"3"` | 12px |
| `"4"` | 16px |
| `"6"` | 24px |
| `"8"` | 32px |

---

## Grid

A CSS Grid container for two-dimensional layouts.

```python
from ContaraNAS.core.ui import Grid, StatCard

Grid(columns=2, gap="4", children=[...])
Grid(columns=4, gap="3", children=[...])
Grid(columns="1fr 2fr", children=[...])  # Custom template
Grid(columns=3, row_height="200px", children=[...])  # Fixed row height
```

### Props

| Prop         | Type                                                   | Default | Description                                    |
|--------------|--------------------------------------------------------|---------|------------------------------------------------|
| `columns`    | `int` or `str`                                         | `2`     | Number of columns or CSS grid-template-columns |
| `gap`        | `"0"`, `"1"`, `"2"`, `"3"`, `"4"`, `"5"`, `"6"`, `"8"` | `"4"`   | Space between grid items                       |
| `row_height` | `str` or `None`                                        | `None`  | CSS value for grid-auto-rows (e.g., "200px")   |
| `children`   | `list[Component]`                                      | `[]`    | Child components                               |

### Column Options

```python
Grid(columns=2, children=[...])  # 2 equal columns
Grid(columns="1fr 2fr", children=[...])  # Second column 2x wider
Grid(columns="200px 1fr", children=[...])  # Fixed + flexible
```

---

## Best Practices

- Use `Stack` for one-dimensional layouts (rows or columns)
- Use `Grid` for two-dimensional layouts (multiple rows and columns)
- Keep gap values consistent within a section
- Don't over-nest layouts (3+ levels deep is usually too much)
