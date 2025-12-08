# Actions

This page explains how to handle user interactions in your ContaraNAS module.

## Overview

Actions are module methods that can be called from the frontend. When a user clicks a button, submits a form, or
triggers any interactive element, an action is invoked.

The action system provides:

- **Decorator-based registration** — Mark methods with `@action`
- **Automatic async handling** — Sync and async methods work the same
- **Auto-commit** — State changes are pushed automatically after actions
- **Structured results** — Return results that control the UI (open modals, show notifications)

## Defining Actions

Use the `@action` decorator to mark a method as callable from the frontend:

```python
from ContaraNAS.core.action import action

class MyModule(Module):
    @action
    async def refresh_data(self) -> None:
        """Refresh data from external source"""
        new_data = await self.fetch_data()
        if self._typed_state:
            self._typed_state.data = new_data
            # Auto-committed by @action decorator
```

### Requirements

1. The method must be a member of a `Module` subclass
2. The method must be decorated with `@action`
3. The method can be sync or async (async recommended)
4. The method name becomes the action identifier

### Sync vs Async

Both sync and async methods work, but async is recommended for I/O operations:

```python
# Async (recommended for I/O)
@action
async def fetch_from_api(self) -> None:
    data = await self.client.get("/data")
    self._typed_state.data = data

# Sync (fine for quick operations)
@action
def increment_counter(self) -> None:
    self._typed_state.counter += 1
```

The `@action` decorator handles both transparently.

## Wiring Actions to UI

Connect actions to interactive components using the `on_click` prop:

```python
from ContaraNAS.core.ui import Button

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

When serialized, the action reference becomes:

```json
{
  "type": "button",
  "label": "Do Something",
  "on_click": {"__action__": "do_something"}
}
```

The frontend uses this to call the correct action when clicked.

## Action Parameters

Actions can accept parameters from the frontend:

```python
@action
async def update_name(self, name: str) -> None:
    """Update the name field"""
    if self._typed_state:
        self._typed_state.name = name

@action
async def set_count(self, count: int = 0) -> None:
    """Set counter to specific value"""
    if self._typed_state:
        self._typed_state.count = count
```

### Form Data

When a button is clicked inside a form, field values are passed as parameters:

```python
from ContaraNAS.core.ui import Stack, Input, Button

# In your UI definition
form = Stack(
    direction="vertical",
    gap="4",
    children=[
        Input(name="username", label="Username"),
        Input(name="password", label="Password", input_type="password"),
        Button(label="Login", on_click=self.login),
    ],
)

# In your action
@action
async def login(self, username: str = "", password: str = "") -> None:
    """Handle login form submission"""
    if not username or not password:
        return Notify(message="Username and password required", variant="error")

    # Perform login...
```

### Type Coercion

Parameter values come from the frontend as strings or basic JSON types. Use type hints and defaults:

```python
@action
async def set_settings(
    self,
    name: str = "",
    count: int = 0,
    enabled: bool = False,
    ratio: float = 1.0,
) -> None:
    """Parameters are coerced to their annotated types"""
    pass
```

## Action Results

Actions can return results that control the frontend behavior.

### Available Results

| Result                     | Purpose              |
|----------------------------|----------------------|
| `OpenModal(modal_id)`      | Open a modal dialog  |
| `CloseModal(modal_id)`     | Close a modal dialog |
| `Notify(message, variant)` | Show a notification  |
| `Refresh()`                | Force UI refresh     |

### Importing Results

```python
from ContaraNAS.core.action import (
    action,
    OpenModal,
    CloseModal,
    Notify,
    Refresh,
)
```

### OpenModal

Open a modal by ID:

```python
@action
async def show_details(self):
    """Open the details modal"""
    return OpenModal(modal_id="game_details")
```

### CloseModal

Close a specific modal or the current modal:

```python
@action
async def save_and_close(self):
    """Save data and close the modal"""
    # Save logic...

    return CloseModal(modal_id="edit_form")

# Or close whatever modal is open
@action
async def cancel(self):
    return CloseModal()  # No modal_id closes current modal
```

### Notify

Show a temporary notification:

```python
@action
async def save_settings(self):
    """Save and notify user"""
    # Save logic...

    return Notify(
        message="Settings saved successfully!",
        variant="success",
    )

@action
async def delete_item(self):
    """Delete with error handling"""
    try:
        await self.do_delete()
        return Notify(message="Item deleted", variant="success")
    except Exception as e:
        return Notify(message=f"Delete failed: {e}", variant="error")
```

#### Notify Props

| Prop      | Type                                                | Default  | Description        |
|-----------|-----------------------------------------------------|----------|--------------------|
| `message` | `str`                                               | Required | Notification text  |
| `variant` | `"info"` \| `"success"` \| `"warning"` \| `"error"` | `"info"` | Notification style |
| `title`   | `str \| None`                                       | `None`   | Optional title     |

### Refresh

Force the UI to refresh:

```python
@action
async def force_refresh(self):
    """Refresh everything"""
    await self.reload_data()
    return Refresh()
```

### Multiple Results

Return a list to trigger multiple results:

```python
@action
async def save_and_close(self) -> list:
    """Save, notify, and close modal"""
    # Save logic...

    return [
        Notify(message="Saved!", variant="success"),
        CloseModal(modal_id="edit_form"),
    ]

@action
async def submit_form(self, **form_data) -> list:
    """Validate, save, and provide feedback"""
    errors = self.validate(form_data)
    if errors:
        return [Notify(message=errors[0], variant="error")]

    await self.save(form_data)

    return [
        Notify(message="Form submitted", variant="success"),
        CloseModal(),
        Refresh(),
    ]
```

## Auto-Commit Behavior

The `@action` decorator automatically commits state if it's dirty:

```python
@action
async def increment(self) -> None:
    """State is auto-committed after this action"""
    if self._typed_state:
        self._typed_state.counter += 1
        # No need to call commit() - it happens automatically
```

This means:

1. Action runs
2. If `self._typed_state.is_dirty` is True, `commit()` is called
3. Commit triggers event to push state to frontend

### When Auto-Commit Happens

Auto-commit occurs **after** the action completes, **before** returning results:

```python
@action
async def update(self) -> Notify:
    self._typed_state.value = 42  # Marks state dirty

    # Auto-commit happens here, before returning

    return Notify(message="Updated!")  # Frontend receives new state + notification
```

### Manual Commit

You can still call `commit()` manually during an action:

```python
@action
async def long_operation(self) -> None:
    """Update progress during operation"""
    for i in range(10):
        await self.process_batch(i)
        self._typed_state.progress = (i + 1) * 10
        self._typed_state.commit()  # Push update immediately

    self._typed_state.progress = 100
    # Final auto-commit happens here
```

## Error Handling

Handle errors gracefully and provide user feedback:

```python
@action
async def risky_operation(self) -> Notify:
    """Operation that might fail"""
    try:
        await self.do_risky_thing()
        return Notify(message="Success!", variant="success")
    except PermissionError:
        return Notify(
            message="Permission denied. Check file permissions.",
            variant="error",
        )
    except ConnectionError:
        return Notify(
            message="Network error. Check your connection.",
            variant="error",
        )
    except Exception as e:
        # Log the full error
        logger.exception("Unexpected error in risky_operation")
        return Notify(
            message="An unexpected error occurred.",
            variant="error",
        )
```

### Updating State on Error

```python
class State(ModuleState):
    error: str | None = None
    loading: bool = False

@action
async def fetch_data(self) -> None:
    """Fetch with error handling"""
    self._typed_state.loading = True
    self._typed_state.error = None
    self._typed_state.commit()

    try:
        data = await self.client.fetch()
        self._typed_state.data = data
    except Exception as e:
        self._typed_state.error = str(e)
    finally:
        self._typed_state.loading = False
        # Auto-committed
```

## Getting Available Actions

The framework can list all actions on a module:

```python
from ContaraNAS.core.action import get_actions

# Get all action methods from a module instance
actions = get_actions(module_instance)
# Returns: {"refresh": <method>, "save": <method>, ...}
```

## Action Dispatcher

The `ActionDispatcher` routes action calls to the correct module:

```python
from ContaraNAS.core.action import ActionDispatcher

dispatcher = ActionDispatcher()

# Register modules
dispatcher.register_module(steam_module)
dispatcher.register_module(sys_monitor_module)

# Dispatch an action
results = await dispatcher.dispatch(
    module_name="steam",
    action_name="refresh_library",
    payload={"force": True},
)
```

This is handled by the framework; you don't need to use it directly.

## Complete Example

```python
from ContaraNAS.core.module import Module, ModuleState
from ContaraNAS.core.action import action, OpenModal, CloseModal, Notify, Refresh
from ContaraNAS.core.ui import Tile, Stat, Button, Modal, Stack, Input

class TaskModule(Module):
    """A simple task management module"""

    class State(ModuleState):
        tasks: list[dict] = []
        loading: bool = False
        error: str | None = None

    async def initialize(self) -> None:
        """Load tasks on startup"""
        await self.load_tasks()

    async def start_monitoring(self) -> None:
        pass

    async def stop_monitoring(self) -> None:
        pass

    async def load_tasks(self) -> None:
        """Load tasks from storage"""
        # Implementation...
        pass

    def get_tile(self) -> Tile:
        state = self._typed_state
        if not state:
            return Tile(icon="check-square", title="Tasks", stats=[])

        pending = sum(1 for t in state.tasks if not t.get("done"))
        completed = sum(1 for t in state.tasks if t.get("done"))

        return Tile(
            icon="check-square",
            title="Tasks",
            stats=[
                Stat(label="Pending", value=pending),
                Stat(label="Completed", value=completed),
                Stat(label="Total", value=len(state.tasks)),
            ],
            actions=[
                Button(label="Add Task", on_click=self.open_add_task),
                Button(label="View All", variant="secondary", on_click=self.open_task_list),
            ],
        )

    # --- Actions ---

    @action
    async def open_add_task(self):
        """Open the add task modal"""
        return OpenModal(modal_id="add_task")

    @action
    async def open_task_list(self):
        """Open the task list modal"""
        return OpenModal(modal_id="task_list")

    @action
    async def add_task(self, title: str = "", description: str = "") -> list:
        """Add a new task"""
        if not title.strip():
            return [Notify(message="Task title is required", variant="error")]

        state = self._typed_state
        if state:
            state.tasks.append({
                "id": len(state.tasks) + 1,
                "title": title.strip(),
                "description": description.strip(),
                "done": False,
            })

        return [
            Notify(message="Task added!", variant="success"),
            CloseModal(modal_id="add_task"),
        ]

    @action
    async def toggle_task(self, task_id: int = 0) -> Notify:
        """Toggle task completion status"""
        state = self._typed_state
        if not state:
            return Notify(message="Module not ready", variant="error")

        for task in state.tasks:
            if task["id"] == task_id:
                task["done"] = not task["done"]
                status = "completed" if task["done"] else "reopened"
                return Notify(message=f"Task {status}", variant="success")

        return Notify(message="Task not found", variant="error")

    @action
    async def delete_task(self, task_id: int = 0) -> Notify:
        """Delete a task"""
        state = self._typed_state
        if not state:
            return Notify(message="Module not ready", variant="error")

        original_len = len(state.tasks)
        state.tasks = [t for t in state.tasks if t["id"] != task_id]

        if len(state.tasks) < original_len:
            return Notify(message="Task deleted", variant="success")
        else:
            return Notify(message="Task not found", variant="error")

    @action
    async def clear_completed(self) -> Notify:
        """Remove all completed tasks"""
        state = self._typed_state
        if not state:
            return Notify(message="Module not ready", variant="error")

        before = len(state.tasks)
        state.tasks = [t for t in state.tasks if not t.get("done")]
        removed = before - len(state.tasks)

        return Notify(message=f"Cleared {removed} completed tasks", variant="success")

    # --- Modals ---

    def get_modals(self) -> list:
        """Return modal definitions"""
        return [
            self._get_add_task_modal(),
            self._get_task_list_modal(),
        ]

    def _get_add_task_modal(self) -> Modal:
        return Modal(
            id="add_task",
            title="Add Task",
            children=[
                Stack(
                    direction="vertical",
                    gap="4",
                    children=[
                        Input(name="title", label="Title", placeholder="Task title..."),
                        Input(name="description", label="Description", placeholder="Optional description..."),
                    ],
                ),
            ],
            footer=[
                Button(label="Cancel", variant="secondary"),
                Button(label="Add", on_click=self.add_task),
            ],
        )

    def _get_task_list_modal(self) -> Modal:
        state = self._typed_state
        tasks = state.tasks if state else []

        return Modal(
            id="task_list",
            title=f"All Tasks ({len(tasks)})",
            children=[
                # Task list would go here
            ],
            footer=[
                Button(label="Clear Completed", variant="secondary", on_click=self.clear_completed),
                Button(label="Close"),
            ],
        )
```

## Best Practices

### Do

- **Use descriptive names** — `refresh_library` not `refresh`
- **Handle errors gracefully** — Always provide user feedback
- **Keep actions focused** — One action, one purpose
- **Use async for I/O** — Database, network, file operations
- **Return appropriate results** — Notify on success/failure

### Don't

- **Don't have side effects without feedback** — If something changes, tell the user
- **Don't forget error handling** — Actions can fail
- **Don't block the event loop** — Use async for slow operations
- **Don't expose internal methods** — Only decorate public actions with `@action`

## See Also

- [State Management](state.md) — How state and commit work
- [Interactive Components](ui/interactive.md) — Buttons and forms
- [Modal Component](ui/modal.md) — OpenModal and CloseModal usage
