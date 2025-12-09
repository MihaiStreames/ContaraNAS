# Declarative UI

This section explains how to build user interfaces for your ContaraNAS module.

## Overview

ContaraNAS uses a **server-driven UI** approach. Instead of writing HTML, CSS, or frontend code, you define your UI in
Python using component classes. The framework serializes these to JSON and the frontend renders them automatically.

```
Python Component → JSON → Frontend Renders
```

This approach provides:

- **Consistency** — All modules look the same (design system)
- **Simplicity** — Write Python, not three languages
- **Type Safety** — Components are Pydantic models with validation
- **Automatic Updates** — State changes re-render the UI

## How It Works

### 1. Define Components in Python

```python
from ContaraNAS.core.ui import Tile, Stat, Button, Stack

tile = Tile(
    icon="gamepad-2",
    title="Steam",
    stats=[
        Stat(label="Games", value=150),
        Stat(label="Size", value="2.3 TB"),
    ],
    actions=[
        Button(label="Refresh", on_click=self.refresh),
    ],
)
```

### 2. Framework Serializes to JSON

```json
{
	"type": "tile",
	"icon": "gamepad-2",
	"title": "Steam",
	"stats": [
		{
			"type": "stat",
			"label": "Games",
			"value": 150
		},
		{
			"type": "stat",
			"label": "Size",
			"value": "2.3 TB"
		}
	],
	"actions": [
		{
			"type": "button",
			"label": "Refresh",
			"on_click": {
				"__action__": "refresh"
			}
		}
	]
}
```

### 3. Frontend Renders the Component

The frontend has a component for each `type` and renders them recursively.

## Component Categories

Components are organized into categories based on their purpose:

| Category                      | Purpose                   | Examples                      |
|-------------------------------|---------------------------|-------------------------------|
| [Layout](layout.md)           | Structure and arrangement | Stack, Grid                   |
| [Card](cards.md)              | Container elements        | Card, Tile, Stat              |
| [Display](display.md)         | Show information          | Text, Progress, Badge, Table  |
| [Interactive](interactive.md) | User input                | Button, Input, Select, Toggle |
| [Modal](modal.md)             | Popup dialogs             | Modal                         |
| [Feedback](feedback.md)       | Status indicators         | Alert, Spinner                |

## Base Component

All components inherit from the `Component` base class:

```python
from pydantic import BaseModel, ConfigDict


class Component(BaseModel):
    """Base class for all UI components"""

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra="forbid",
    )

    _type: ClassVar[str] = "component"

    def to_dict(self) -> dict[str, Any]:
        """Serialize component to dictionary for frontend"""
        ...
```

### Key Methods

| Method                | Description                                       |
|-----------------------|---------------------------------------------------|
| `to_dict()`           | Serialize the component to a JSON-compatible dict |
| `_serialize_value()`  | Handle nested components and special types        |
| `_serialize_action()` | Convert callable actions to references            |

### The `_type` Field

Every component has a `_type` class variable that identifies it to the frontend:

```python
class Button(Component):
    _type: ClassVar[str] = "button"
```

This becomes `{"type": "button", ...}` in the serialized output.

## Imports

All components are exported from `ContaraNAS.core.ui`:

```python
from ContaraNAS.core.ui import (
    # Layout
    Stack,
    Grid,

    # Cards
    Card,
    Tile,
    Stat,

    # Display
    Text,
    StatSmall,
    StatCard,
    Progress,
    SegmentedProgress,
    SegmentedProgressSegment,
    Badge,
    Table,
    TableColumn,
    LineChart,
    Image,

    # Interactive
    Button,
    Input,
    Select,
    SelectOption,
    Toggle,
    Checkbox,
    Tabs,
    Tab,

    # Modal
    Modal,

    # Feedback
    Alert,
    Spinner,
)
```

## Building a Tile

Every module provides a tile for the dashboard via `get_tile()`. See [Card Components - Tile](cards.md#tile) for the
full Tile API and examples.

## Nesting Components

Components can contain other components. The `children` prop accepts a list of components:

```python
from ContaraNAS.core.ui import Stack, Text, Button

content = Stack(
    direction="vertical",
    gap="4",
    children=[
        Text(content="Welcome to the module!"),
        Text(content="Click below to get started.", variant="secondary"),
        Stack(
            direction="horizontal",
            gap="2",
            children=[
                Button(label="Start", variant="primary"),
                Button(label="Cancel", variant="secondary"),
            ],
        ),
    ],
)
```

This serializes to a nested JSON structure that the frontend renders recursively.

## Actions in Components

Interactive components like Button can reference module methods:

```python
class MyModule(Module):
    @action
    async def do_something(self) -> None:
        pass

    def get_tile(self) -> Tile:
        return Tile(
            icon="box",
            title="My Module",
            actions=[
                Button(label="Do Something", on_click=self.do_something),
            ],
        )
```

The method reference is serialized as:

```json
{
	"type": "button",
	"label": "Do Something",
	"on_click": {
		"__action__": "do_something"
	}
}
```

The frontend uses this to call the correct action endpoint when clicked.

See [Actions](../actions.md) for full details.

## Common Patterns

### Conditional Content

Show different content based on state:

```python
def get_tile(self) -> Tile:
    state = self._typed_state
    if not state:
        return Tile(icon="box", title="Module", stats=[])

    # Show error in content if present
    content = None
    if state.error:
        content = [Alert(message=state.error, variant="error")]

    return Tile(
        icon="box",
        title="Module",
        stats=[...],
        content=content,
    )
```

### Dynamic Lists

Render lists from state:

```python
def get_tile(self) -> Tile:
    state = self._typed_state
    items = state.items if state else []

    return Tile(
        icon="clipboard-list",
        title="Tasks",
        stats=[
            Stat(label="Total", value=len(items)),
            Stat(label="Completed", value=sum(1 for i in items if i["done"])),
        ],
        content=[
            Stack(
                direction="vertical",
                children=[
                    Text(content=item["name"])
                    for item in items[:5]  # Show first 5
                ],
            ),
        ],
    )
```

### Loading States

Show loading indicators during async operations. See [Feedback Components](feedback.md#loading-states) for detailed
patterns with Spinner.

## Best Practices

### Do

- **Keep tiles simple** — Show key stats and primary actions only
- **Use consistent icons** — Use [Lucide](https://lucide.dev/icons/) icon names only
- **Provide loading states** — Users should know when something is happening
- **Handle errors gracefully** — Show meaningful error messages
- **Use semantic variants** — `"error"` for errors, `"warning"` for warnings

### Don't

- **Don't overcrowd tiles** — Details belong in modals
- **Don't nest too deeply** — Keep component trees shallow
- **Don't duplicate the frontend** — Let the design system handle styling
- **Don't put secrets in UI** — Component data is sent to the client

## Next Steps

- [Layout Components](layout.md) — Stack, Grid
- [Card Components](cards.md) — Card, Tile, Stat
- [Display Components](display.md) — Text, Progress, Badge, Table
- [Interactive Components](interactive.md) — Button, Input, Select, Toggle
- [Modal](modal.md) — Popup dialogs
- [Feedback Components](feedback.md) — Alert, Spinner
