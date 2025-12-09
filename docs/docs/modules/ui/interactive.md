# Interactive Components

Interactive components accept user input and trigger actions.

## Button

A clickable button that triggers an action.

```python
from ContaraNAS.core.ui import Button

Button(label="Save", on_click=self.save_settings, variant="primary")
Button(label="Cancel", variant="secondary")
Button(label="Delete", variant="danger", icon="Trash2")
Button(label="Saving...", loading=True, disabled=True)
Button(label="Settings", icon="Settings", icon_only=True)  # Icon-only button
```

### Props

| Prop        | Type                                              | Default     | Description                  |
|-------------|---------------------------------------------------|-------------|------------------------------|
| `label`     | `str`                                             | Required    | Button text                  |
| `on_click`  | `Callable` or `None`                              | `None`      | Action to call when clicked  |
| `variant`   | `"primary"`, `"secondary"`, `"ghost"`, `"danger"` | `"primary"` | Visual style                 |
| `size`      | `"sm"`, `"md"`, `"lg"`                            | `"md"`      | Button size                  |
| `icon`      | `str` or `None`                                   | `None`      | Lucide icon name             |
| `icon_only` | `bool`                                            | `False`     | Show only icon (hides label) |
| `disabled`  | `bool`                                            | `False`     | Disable the button           |
| `loading`   | `bool`                                            | `False`     | Show loading spinner         |

### Variants

| Variant       | Use Case                             |
|---------------|--------------------------------------|
| `"primary"`   | Main action, submit buttons          |
| `"secondary"` | Alternative actions, cancel buttons  |
| `"ghost"`     | Subtle actions, links                |
| `"danger"`    | Destructive actions (delete, remove) |

---

## Input

A text input field.

```python
from ContaraNAS.core.ui import Input

Input(name="username", label="Username")
Input(name="search", placeholder="Search...")
Input(name="password", label="Password", input_type="password")
Input(name="count", label="Count", input_type="number")
```

### Props

| Prop          | Type                                          | Default  | Description                          |
|---------------|-----------------------------------------------|----------|--------------------------------------|
| `name`        | `str`                                         | Required | Field name (used in form submission) |
| `label`       | `str` or `None`                               | `None`   | Label text above input               |
| `value`       | `str`                                         | `""`     | Initial value                        |
| `input_type`  | `"text"`, `"password"`, `"email"`, `"number"` | `"text"` | Input type                           |
| `placeholder` | `str` or `None`                               | `None`   | Placeholder text                     |
| `disabled`    | `bool`                                        | `False`  | Disable the input                    |

---

## Select

A dropdown selection input.

```python
from ContaraNAS.core.ui import Select, SelectOption

Select(
    name="library",
    label="Select Library",
    options=[
        SelectOption(value="lib1", label="Main Library"),
        SelectOption(value="lib2", label="Games"),
    ],
    value="lib1",
)
```

### Select Props

| Prop       | Type                 | Default  | Description              |
|------------|----------------------|----------|--------------------------|
| `name`     | `str`                | Required | Field name               |
| `label`    | `str` or `None`      | `None`   | Label text               |
| `options`  | `list[SelectOption]` | Required | Available options        |
| `value`    | `str` or `None`      | `None`   | Currently selected value |
| `disabled` | `bool`               | `False`  | Disable the select       |

### SelectOption Props

| Prop    | Type  | Default  | Description             |
|---------|-------|----------|-------------------------|
| `value` | `str` | Required | Value sent on selection |
| `label` | `str` | Required | Display text            |

---

## Toggle

A boolean switch input.

```python
from ContaraNAS.core.ui import Toggle

Toggle(name="notifications", label="Enable Notifications")
Toggle(name="auto_update", label="Auto Update", checked=True)
Toggle(name="feature", label="Experimental Feature", disabled=True)
```

### Props

| Prop       | Type            | Default  | Description          |
|------------|-----------------|----------|----------------------|
| `name`     | `str`           | Required | Field name           |
| `label`    | `str` or `None` | `None`   | Label text           |
| `checked`  | `bool`          | `False`  | Whether toggle is on |
| `disabled` | `bool`          | `False`  | Disable the toggle   |

---

## Checkbox

A boolean checkbox input, similar to Toggle but with different styling.

```python
from ContaraNAS.core.ui import Checkbox

Checkbox(name="agree", label="I agree to the terms")
Checkbox(name="remember", label="Remember me", checked=True)
```

### Props

| Prop       | Type            | Default  | Description                 |
|------------|-----------------|----------|-----------------------------|
| `name`     | `str`           | Required | Field name                  |
| `label`    | `str` or `None` | `None`   | Label text                  |
| `checked`  | `bool`          | `False`  | Whether checkbox is checked |
| `disabled` | `bool`          | `False`  | Disable the checkbox        |

### Toggle vs Checkbox

- **Toggle** — Settings that take effect immediately, on/off states
- **Checkbox** — Form inputs that submit together, multiple selections

---

## Tabs

A tabbed container for organizing content into switchable panels.

```python
from ContaraNAS.core.ui import Tabs, Tab, Text, Progress

Tabs(
    tabs=[
        Tab(id="cpu", label="CPU", icon="Cpu", children=[...]),
        Tab(id="memory", label="Memory", icon="MemoryStick", children=[...]),
    ],
    default_tab="cpu",
    size="sm",
)
```

### Tabs Props

| Prop          | Type            | Default  | Description                  |
|---------------|-----------------|----------|------------------------------|
| `tabs`        | `list[Tab]`     | Required | List of Tab components       |
| `default_tab` | `str` or `None` | `None`   | ID of tab to show by default |
| `size`        | `"sm"`, `"md"`  | `"md"`   | Tab button size              |

### Tab Props

| Prop       | Type              | Default  | Description       |
|------------|-------------------|----------|-------------------|
| `id`       | `str`             | Required | Unique identifier |
| `label`    | `str`             | Required | Tab button text   |
| `icon`     | `str` or `None`   | `None`   | Lucide icon name  |
| `children` | `list[Component]` | `[]`     | Tab panel content |

---

## Form Submissions

The `name` prop on Input, Select, Toggle, and Checkbox determines parameter names in your action:

```python
@action
async def save_settings(self, server: str = "", auto_refresh: bool = False) -> None:
    # server comes from Input(name="server", ...)
    # auto_refresh comes from Toggle(name="auto_refresh", ...)
    pass
```

See [Actions](../actions.md#form-data) for more details.
