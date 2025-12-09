# Modal Component

Modals are popup dialogs for detailed views, forms, and confirmations.

## Overview

Modals are used when you need to:

- Show detailed information that doesn't fit in a tile
- Collect user input through forms
- Confirm destructive actions
- Display lists or tables of data

## Basic Usage

```python
from ContaraNAS.core.ui import Modal, Stack, Text, Button

modal = Modal(
    id="my_modal",
    title="Modal Title",
    children=[
        Text(content="This is the modal content."),
        Text(content="You can put any components here.", variant="secondary"),
    ],
    footer=[
        Button(label="Close", variant="secondary"),
    ],
)
```

### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `id` | `str` | Required | Unique identifier for the modal |
| `title` | `str` | Required | Modal header title |
| `children` | `list[Component]` | `[]` | Main content components |
| `footer` | `list[Component]` or `None` | `None` | Footer components (usually buttons) |
| `closable` | `bool` | `True` | Show close button in header |

## Opening Modals

To open a modal, return an `OpenModal` result from an action:

```python
from ContaraNAS.core.action import action, OpenModal

class MyModule(Module):
    @action
    async def show_details(self):
        """Open the details modal."""
        return OpenModal(modal_id="details_modal")
```

Wire the action to a button:

```python
Button(label="Details", on_click=self.show_details)
```

## Closing Modals

### Automatic Close

Buttons without `on_click` automatically close the modal:

```python
Modal(
    id="confirm",
    title="Confirm",
    children=[...],
    footer=[
        Button(label="Cancel", variant="secondary"),  # Closes modal
    ],
)
```

### Programmatic Close

Return `CloseModal` from an action:

```python
from ContaraNAS.core.action import action, CloseModal, Notify

@action
async def save_and_close(self) -> list:
    """Save data and close the modal"""
    # Save logic here...

    return [
        Notify(message="Saved successfully!", variant="success"),
        CloseModal(modal_id="edit_modal"),
    ]
```

## Modal Patterns

### Confirmation Dialog

```python
Modal(
    id="delete_confirm",
    title="Delete Item?",
    children=[
        Text(content="Are you sure? This action cannot be undone."),
    ],
    footer=[
        Button(label="Cancel", variant="secondary"),
        Button(label="Delete", variant="danger", on_click=self.delete_item),
    ],
)
```

### Form Modal

```python
Modal(
    id="edit_settings",
    title="Edit Settings",
    children=[
        Stack(direction="vertical", gap="4", children=[
            Input(name="name", label="Name", value=state.name),
            Select(name="category", label="Category", options=[...], value=state.category),
        ]),
    ],
    footer=[
        Button(label="Cancel", variant="secondary"),
        Button(label="Save", on_click=self.save_settings),
    ],
)
```

Form field values are passed to your action. See [Actions - Form Data](../actions.md#form-data).

## Providing Modals

Implement `get_modals()` in your module to provide modals:

```python
def get_modals(self) -> list[Modal]:
    return [self.get_details_modal(), self.get_delete_modal()]
```

## Best Practices

- Use descriptive IDs (`"game_details"` not `"modal1"`)
- Include cancel options in footer
- Keep modals focused — one purpose per modal
- Use `"danger"` variant for destructive actions
- Don't nest modals — one at a time

## See Also

- [Actions](../actions.md) — OpenModal and CloseModal results
- [Interactive Components](interactive.md) — Form elements for modals
