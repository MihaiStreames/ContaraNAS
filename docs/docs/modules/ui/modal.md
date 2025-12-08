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
| `footer` | `list[Component] \| None` | `None` | Footer components (usually buttons) |
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
    """Save data and close the modal."""
    # Save logic here...

    return [
        Notify(message="Saved successfully!", variant="success"),
        CloseModal(modal_id="edit_modal"),
    ]
```

## Modal Patterns

### Confirmation Dialog

```python
from ContaraNAS.core.ui import Modal, Text, Stack, Button
from ContaraNAS.core.action import action, CloseModal, Notify

class MyModule(Module):
    @action
    async def confirm_delete(self):
        return OpenModal(modal_id="delete_confirm")

    @action
    async def delete_item(self) -> list:
        # Perform deletion
        await self.do_delete()

        return [
            Notify(message="Item deleted", variant="success"),
            CloseModal(modal_id="delete_confirm"),
        ]

    def get_delete_modal(self) -> Modal:
        return Modal(
            id="delete_confirm",
            title="Delete Item?",
            children=[
                Text(content="Are you sure you want to delete this item?"),
                Text(
                    content="This action cannot be undone.",
                    variant="secondary"
                ),
            ],
            footer=[
                Button(label="Cancel", variant="secondary"),
                Button(label="Delete", variant="danger", on_click=self.delete_item),
            ],
        )
```

### Form Modal

```python
from ContaraNAS.core.ui import Modal, Stack, Input, Select, SelectOption, Button

def get_edit_modal(self) -> Modal:
    state = self._typed_state

    return Modal(
        id="edit_settings",
        title="Edit Settings",
        children=[
            Stack(
                direction="vertical",
                gap="4",
                children=[
                    Input(
                        name="name",
                        label="Name",
                        value=state.name if state else "",
                    ),
                    Select(
                        name="category",
                        label="Category",
                        options=[
                            SelectOption(value="a", label="Category A"),
                            SelectOption(value="b", label="Category B"),
                        ],
                        value=state.category if state else "a",
                    ),
                    Input(
                        name="description",
                        label="Description",
                        value=state.description if state else "",
                    ),
                ],
            ),
        ],
        footer=[
            Button(label="Cancel", variant="secondary"),
            Button(label="Save", on_click=self.save_settings),
        ],
    )
```

The `save_settings` action receives form field values as parameters. See [Actions - Form Data](../actions.md#form-data) for details.

### Detail View Modal

```python
from ContaraNAS.core.ui import Modal, Stack, Text, Table, TableColumn, Badge

def get_game_details_modal(self, game_id: str) -> Modal:
    game = self.get_game(game_id)
    if not game:
        return Modal(
            id="game_details",
            title="Not Found",
            children=[Text(content="Game not found.")],
        )

    return Modal(
        id="game_details",
        title=game.name,
        children=[
            Stack(
                direction="vertical",
                gap="4",
                children=[
                    # Header with badge
                    Stack(
                        direction="horizontal",
                        gap="2",
                        align="center",
                        children=[
                            Text(content=game.name),
                            Badge(
                                text="Installed" if game.installed else "Not Installed",
                                variant="success" if game.installed else "default",
                            ),
                        ],
                    ),

                    # Info section
                    Stack(
                        direction="vertical",
                        gap="1",
                        children=[
                            Text(content=f"Size: {game.size}", variant="secondary"),
                            Text(content=f"Path: {game.path}", variant="code"),
                            Text(content=f"Last played: {game.last_played}", variant="muted"),
                        ],
                    ),

                    # DLC table
                    Text(content="DLC"),
                    Table(
                        columns=[
                            TableColumn(key="name", label="Name"),
                            TableColumn(key="size", label="Size", align="right"),
                        ],
                        data=[
                            {"name": dlc.name, "size": dlc.size}
                            for dlc in game.dlc
                        ],
                        empty_message="No DLC installed",
                    ),
                ],
            ),
        ],
        footer=[
            Button(label="Close", variant="secondary"),
            Button(label="Uninstall", variant="danger", on_click=self.uninstall_game),
        ],
    )
```

### List Modal

```python
from ContaraNAS.core.ui import Modal, Table, TableColumn, Button

def get_games_list_modal(self) -> Modal:
    state = self._typed_state
    games = state.games if state else []

    return Modal(
        id="games_list",
        title=f"All Games ({len(games)})",
        children=[
            Table(
                columns=[
                    TableColumn(key="name", label="Name"),
                    TableColumn(key="size", label="Size", width="100px", align="right"),
                    TableColumn(key="library", label="Library"),
                ],
                data=[
                    {
                        "name": game.name,
                        "size": format_size(game.size),
                        "library": game.library_name,
                    }
                    for game in games
                ],
                empty_message="No games found",
            ),
        ],
        footer=[
            Button(label="Close", variant="secondary"),
            Button(label="Refresh", on_click=self.refresh_games),
        ],
    )
```

## Providing Modals

Modals are defined in your module and provided to the frontend:

```python
class MyModule(Module):
    def get_tile(self) -> Tile:
        return Tile(
            icon="package",
            title="My Module",
            stats=[...],
            actions=[
                Button(label="Details", on_click=self.open_details),
            ],
        )

    @action
    async def open_details(self):
        return OpenModal(modal_id="details")

    # Module provides its modals
    def get_modals(self) -> list[Modal]:
        return [
            self.get_details_modal(),
            self.get_delete_confirm_modal(),
        ]
```

## Best Practices

### Do

- **Use descriptive IDs** — `"game_details"` not `"modal1"`
- **Provide clear titles** — Tell users what they're looking at
- **Include cancel options** — Users should be able to dismiss without action
- **Keep modals focused** — One purpose per modal
- **Use appropriate button variants** — `"danger"` for destructive actions

### Don't

- **Don't nest modals** — Open one modal at a time
- **Don't overload content** — If it's too complex, consider a separate page
- **Don't forget loading states** — Show spinners during async operations
- **Don't hide critical information** — Important data should be visible on the tile

## Modal IDs

Modal IDs must be unique within your module. Use a consistent naming scheme:

```python
# Good - descriptive and consistent
"game_details"
"library_settings"
"delete_confirmation"
"add_library_form"

# Avoid - unclear or generic
"modal1"
"popup"
"form"
```

## See Also

- [Actions](../actions.md) — OpenModal and CloseModal results
- [Interactive Components](interactive.md) — Form elements for modals
- [Layout Components](layout.md) — Organizing modal content
