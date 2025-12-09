# Interactive Components

Interactive components accept user input and trigger actions.

## Button

A clickable button that triggers an action.

```python
from ContaraNAS.core.ui import Button, Tile
from ContaraNAS.core.action import action

class MyModule(Module):
    @action
    async def save_settings(self) -> None:
        # Handle save
        pass

    def get_tile(self) -> Tile:
        return Tile(
            icon="settings",
            title="Settings",
            actions=[
                Button(label="Save", on_click=self.save_settings, variant="primary"),
            ],
        )
```

### Props

| Prop       | Type                                                    | Default     | Description                 |
|------------|---------------------------------------------------------|-------------|-----------------------------|
| `label`    | `str`                                                   | Required    | Button text                 |
| `on_click` | `Callable \| None`                                      | `None`      | Action to call when clicked |
| `variant`  | `"primary"` \| `"secondary"` \| `"ghost"` \| `"danger"` | `"primary"` | Visual style                |
| `size`     | `"sm"` \| `"md"` \| `"lg"`                              | `"md"`      | Button size                 |
| `icon`     | `str \| None`                                           | `None`      | Lucide icon name            |
| `disabled` | `bool`                                                  | `False`     | Disable the button          |
| `loading`  | `bool`                                                  | `False`     | Show loading spinner        |

### Variants

| Variant       | Use Case                             |
|---------------|--------------------------------------|
| `"primary"`   | Main action, submit buttons          |
| `"secondary"` | Alternative actions, cancel buttons  |
| `"ghost"`     | Subtle actions, links                |
| `"danger"`    | Destructive actions (delete, remove) |

```python
# Primary action
Button(label="Save", variant="primary")

# Secondary action
Button(label="Cancel", variant="secondary")

# Ghost/subtle button
Button(label="Learn more", variant="ghost")

# Dangerous action
Button(label="Delete", variant="danger")
```

### Sizes

```python
Button(label="Small", size="sm")
Button(label="Medium", size="md")  # Default
Button(label="Large", size="lg")
```

### With Icons

```python
Button(label="Refresh", icon="refresh-cw")
Button(label="Download", icon="download")
Button(label="Delete", icon="trash-2", variant="danger")
```

### States

```python
# Disabled button
Button(label="Submit", disabled=True)

# Loading button
Button(label="Saving...", loading=True, disabled=True)
```

### Loading State

Use the `loading` and `disabled` props together during async operations:

```python
Button(
    label="Saving..." if state.saving else "Save",
    on_click=self.save,
    loading=state.saving,
    disabled=state.saving,
)
```

See [Feedback Components](feedback.md#loading-states) for the full loading state pattern with state management.

---

## Input

A text input field.

```python
from ContaraNAS.core.ui import Input

# Basic text input
Input(name="username", label="Username")

# With placeholder
Input(name="search", placeholder="Search...")

# With initial value
Input(name="name", label="Name", value="John")

# Password input
Input(name="password", label="Password", input_type="password")

# Email input
Input(name="email", label="Email", input_type="email")

# Number input
Input(name="count", label="Count", input_type="number")
```

### Props

| Prop          | Type                                                | Default  | Description                          |
|---------------|-----------------------------------------------------|----------|--------------------------------------|
| `name`        | `str`                                               | Required | Field name (used in form submission) |
| `label`       | `str \| None`                                       | `None`   | Label text above input               |
| `value`       | `str`                                               | `""`     | Initial value                        |
| `input_type`  | `"text"` \| `"password"` \| `"email"` \| `"number"` | `"text"` | Input type                           |
| `placeholder` | `str \| None`                                       | `None`   | Placeholder text                     |
| `disabled`    | `bool`                                              | `False`  | Disable the input                    |

### Input Types

| Type         | Description           |
|--------------|-----------------------|
| `"text"`     | General text input    |
| `"password"` | Masked password input |
| `"email"`    | Email with validation |
| `"number"`   | Numeric input         |

### Form Example

```python
from ContaraNAS.core.ui import Stack, Input, Button

form = Stack(
    direction="vertical",
    gap="4",
    children=[
        Input(name="server", label="Server URL", placeholder="https://..."),
        Input(name="username", label="Username"),
        Input(name="password", label="Password", input_type="password"),
        Stack(
            direction="horizontal",
            gap="2",
            justify="end",
            children=[
                Button(label="Cancel", variant="secondary"),
                Button(label="Connect", on_click=self.connect),
            ],
        ),
    ],
)
```

---

## Select

A dropdown selection input.

```python
from ContaraNAS.core.ui import Select, SelectOption

select = Select(
    name="library",
    label="Select Library",
    options=[
        SelectOption(value="lib1", label="Main Library"),
        SelectOption(value="lib2", label="Games"),
        SelectOption(value="lib3", label="External Drive"),
    ],
    value="lib1",  # Pre-selected value
)
```

### Select Props

| Prop       | Type                 | Default  | Description              |
|------------|----------------------|----------|--------------------------|
| `name`     | `str`                | Required | Field name               |
| `label`    | `str \| None`        | `None`   | Label text               |
| `options`  | `list[SelectOption]` | Required | Available options        |
| `value`    | `str \| None`        | `None`   | Currently selected value |
| `disabled` | `bool`               | `False`  | Disable the select       |

### SelectOption Props

| Prop    | Type  | Default  | Description             |
|---------|-------|----------|-------------------------|
| `value` | `str` | Required | Value sent on selection |
| `label` | `str` | Required | Display text            |

### Dynamic Options

Build options from state:

```python
options = [
    SelectOption(value=lib.id, label=lib.name)
    for lib in state.libraries
]

select = Select(
    name="library",
    label="Library",
    options=options,
    value=state.selected_library,
)
```

---

## Toggle

A boolean switch input.

```python
from ContaraNAS.core.ui import Toggle

# Basic toggle
Toggle(name="notifications", label="Enable Notifications")

# Pre-checked toggle
Toggle(name="auto_update", label="Auto Update", checked=True)

# Disabled toggle
Toggle(name="feature", label="Experimental Feature", disabled=True)
```

### Props

| Prop       | Type          | Default  | Description          |
|------------|---------------|----------|----------------------|
| `name`     | `str`         | Required | Field name           |
| `label`    | `str \| None` | `None`   | Label text           |
| `checked`  | `bool`        | `False`  | Whether toggle is on |
| `disabled` | `bool`        | `False`  | Disable the toggle   |

### Example: Settings Form

```python
from ContaraNAS.core.ui import Stack, Toggle, Button

settings_form = Stack(
    direction="vertical",
    gap="3",
    children=[
        Toggle(
            name="auto_refresh",
            label="Auto-refresh data",
            checked=state.auto_refresh,
        ),
        Toggle(
            name="notifications",
            label="Show notifications",
            checked=state.notifications,
        ),
        Toggle(
            name="dark_mode",
            label="Dark mode",
            checked=state.dark_mode,
        ),
        Button(label="Save Settings", on_click=self.save_settings),
    ],
)
```

---

## Checkbox

A boolean checkbox input, similar to Toggle but with different styling.

```python
from ContaraNAS.core.ui import Checkbox

# Basic checkbox
Checkbox(name="agree", label="I agree to the terms")

# Pre-checked
Checkbox(name="remember", label="Remember me", checked=True)

# Disabled
Checkbox(name="locked", label="Locked option", checked=True, disabled=True)
```

### Props

| Prop       | Type          | Default  | Description                 |
|------------|---------------|----------|-----------------------------|
| `name`     | `str`         | Required | Field name                  |
| `label`    | `str \| None` | `None`   | Label text                  |
| `checked`  | `bool`        | `False`  | Whether checkbox is checked |
| `disabled` | `bool`        | `False`  | Disable the checkbox        |

### Toggle vs Checkbox

Use **Toggle** for:

- Settings that take effect immediately
- On/off states
- Feature flags

Use **Checkbox** for:

- Form inputs that submit together
- Multiple selections from a list
- Agreements and confirmations

### Multiple Checkboxes

```python
from ContaraNAS.core.ui import Stack, Checkbox, Text

selection = Stack(
    direction="vertical",
    gap="2",
    children=[
        Text(content="Select games to include:"),
        Checkbox(name="game_a", label="Game A (50 GB)", checked=True),
        Checkbox(name="game_b", label="Game B (25 GB)", checked=False),
        Checkbox(name="game_c", label="Game C (100 GB)", checked=True),
    ],
)
```

---

## Tabs

A tabbed container for organizing content into switchable panels.

```python
from ContaraNAS.core.ui import Tabs, Tab, Text, Progress

tabs = Tabs(
    tabs=[
        Tab(
            id="cpu",
            label="CPU",
            icon="Cpu",
            children=[
                Text(content="CPU usage information"),
                Progress(value=45, max=100, label="45%"),
            ],
        ),
        Tab(
            id="memory",
            label="Memory",
            icon="MemoryStick",
            children=[
                Text(content="Memory usage information"),
                Progress(value=72, max=100, label="72%"),
            ],
        ),
    ],
    default_tab="cpu",
)
```

### Tabs Props

| Prop          | Type         | Default | Description                      |
|---------------|--------------|---------|----------------------------------|
| `tabs`        | `list[Tab]`  | Required| List of Tab components           |
| `default_tab` | `str \| None`| `None`  | ID of tab to show by default     |
| `size`        | `"sm"` \| `"md"` | `"md"` | Tab button size               |

### Tab Props

| Prop       | Type              | Default  | Description              |
|------------|-------------------|----------|--------------------------|
| `id`       | `str`             | Required | Unique identifier        |
| `label`    | `str`             | Required | Tab button text          |
| `icon`     | `str \| None`     | `None`   | Lucide icon name         |
| `children` | `list[Component]` | `[]`     | Tab panel content        |

### Dynamic Tabs

Build tabs from state:

```python
def build_disk_tabs(disks: list[dict]) -> Tabs:
    tabs = []
    for i, disk in enumerate(disks):
        tabs.append(
            Tab(
                id=f"disk_{i}",
                label=disk["device"].split("/")[-1],
                icon="HardDrive",
                children=[
                    Text(content=disk["mountpoint"]),
                    Progress(
                        value=disk["usage_percent"],
                        max=100,
                        label=f"{disk['usage_percent']:.0f}%",
                    ),
                ],
            )
        )

    return Tabs(tabs=tabs, default_tab="disk_0")
```

### Example: System Monitor Tile

```python
def get_tile(self) -> Tile:
    return Tile(
        icon="Activity",
        title="System Monitor",
        colspan=2,  # Wide tile
        content=[
            Tabs(
                tabs=[
                    Tab(id="cpu", label="CPU", icon="Cpu", children=[...]),
                    Tab(id="memory", label="Memory", icon="MemoryStick", children=[...]),
                    Tab(id="disk_0", label="nvme0n1", icon="HardDrive", children=[...]),
                ],
                default_tab="cpu",
                size="sm",
            )
        ],
    )
```

---

## Handling Form Submissions

When a button with `on_click` is clicked, the form data is collected and sent to your action:

```python
class MyModule(Module):
    @action
    async def save_settings(
        self,
        server: str = "",
        username: str = "",
        password: str = "",
        auto_refresh: bool = False,
    ) -> None:
        """Handle form submission"""
        if not server or not username:
            from ContaraNAS.core.action import Notify
            return Notify(message="Server and username required", variant="error")

        # Save settings
        if self._typed_state:
            self._typed_state.server = server
            self._typed_state.username = username
            self._typed_state.auto_refresh = auto_refresh
            # Password handling...

        from ContaraNAS.core.action import Notify
        return Notify(message="Settings saved!", variant="success")
```

!!! note "Form Data Mapping"
    The `name` prop on Input, Select, Toggle, and Checkbox components determines the parameter name in your action method.

---

## See Also

- [Modal Component](modal.md#form-modal) — Complete form example inside a modal
- [Actions](../actions.md#form-data) — How form data is passed to actions
