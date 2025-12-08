# Feedback Components

Feedback components communicate status, progress, and system messages to users.

## Alert

Displays a message with semantic meaning (info, success, warning, error).

```python
from ContaraNAS.core.ui import Alert

# Info alert
Alert(message="Your library is being scanned.", variant="info")

# Success alert
Alert(message="Settings saved successfully!", variant="success")

# Warning alert
Alert(
    message="Disk space is running low.",
    variant="warning",
    title="Warning"
)

# Error alert
Alert(
    message="Failed to connect to server. Check your network settings.",
    variant="error",
    title="Connection Error"
)
```

### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `message` | `str` | Required | Alert message text |
| `variant` | `"info"` \| `"success"` \| `"warning"` \| `"error"` | `"info"` | Visual style and meaning |
| `title` | `str \| None` | `None` | Optional title/heading |

### Variants

| Variant | Use Case | Color |
|---------|----------|-------|
| `"info"` | General information, tips | Blue |
| `"success"` | Completed actions, positive feedback | Green |
| `"warning"` | Caution, non-critical issues | Yellow/Orange |
| `"error"` | Errors, failures, critical issues | Red |

### With Title

Add a title for more prominent alerts:

```python
Alert(
    title="Update Available",
    message="A new version of ContaraNAS is available. Restart to update.",
    variant="info",
)

Alert(
    title="Backup Complete",
    message="All 150 games have been backed up to external storage.",
    variant="success",
)

Alert(
    title="Storage Warning",
    message="Less than 10 GB remaining on primary drive.",
    variant="warning",
)

Alert(
    title="Sync Failed",
    message="Could not sync with cloud storage. Error: Connection timeout.",
    variant="error",
)
```

### Common Patterns

**Error Display in Tiles:**

```python
def get_tile(self) -> Tile:
    state = self._typed_state
    if not state:
        return Tile(icon="box", title="Module", stats=[])

    # Show error in tile content if present
    content = None
    if state.error:
        content = [Alert(title="Error", message=state.error, variant="error")]

    return Tile(
        icon="box",
        title="Module",
        stats=[...],
        content=content,
    )
```

**Status Messages in Modals:**

```python
from ContaraNAS.core.ui import Modal, Stack, Alert, Text

def get_status_modal(self) -> Modal:
    state = self._typed_state
    status = state.sync_status if state else "unknown"

    if status == "syncing":
        alert = Alert(message="Sync in progress...", variant="info")
    elif status == "complete":
        alert = Alert(message="Sync complete!", variant="success")
    elif status == "failed":
        alert = Alert(
            title="Sync Failed",
            message=state.sync_error or "Unknown error",
            variant="error",
        )
    else:
        alert = None

    return Modal(
        id="sync_status",
        title="Sync Status",
        children=[alert] if alert else [Text(content="No sync in progress.")],
    )
```

---

## Spinner

A loading indicator for async operations.

```python
from ContaraNAS.core.ui import Spinner

# Basic spinner
Spinner()

# With label
Spinner(label="Loading...")

# Different sizes
Spinner(size="sm")
Spinner(size="md")  # Default
Spinner(size="lg")
```

### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `size` | `"sm"` \| `"md"` \| `"lg"` | `"md"` | Spinner size |
| `label` | `str \| None` | `None` | Text shown below spinner |

### Sizes

| Size | Use Case |
|------|----------|
| `"sm"` | Inline loading, buttons |
| `"md"` | General loading states |
| `"lg"` | Full-page or modal loading |

### Loading States

**In Tiles:**

```python
def get_tile(self) -> Tile:
    state = self._typed_state
    if not state:
        return Tile(icon="box", title="Module", stats=[])

    # Show loading spinner in content
    content = None
    if state.loading:
        content = [Spinner(size="lg", label="Scanning libraries...")]

    return Tile(
        icon="box",
        title="Module",
        stats=[...],
        content=content,
    )
```

**In Modals:**

```python
def get_data_modal(self) -> Modal:
    state = self._typed_state
    loading = state.modal_loading if state else False

    if loading:
        content = [
            Stack(
                direction="vertical",
                align="center",
                gap="4",
                children=[
                    Spinner(size="lg"),
                    Text(content="Fetching data...", variant="secondary"),
                ],
            ),
        ]
    else:
        content = [
            Table(columns=[...], data=state.data),
        ]

    return Modal(
        id="data_view",
        title="Data",
        children=content,
    )
```

**Inline in Content:**

```python
Stack(
    direction="horizontal",
    gap="2",
    align="center",
    children=[
        Spinner(size="sm"),
        Text(content="Checking for updates..."),
    ],
)
```

---

## Alert vs Notify

`Alert` is a UI component. `Notify` is an action result (see [Actions - Notify](../actions.md#notify)).

| Feature | Alert (Component) | Notify (Action Result) |
|---------|-------------------|------------------------|
| Location | Embedded in UI | Toast/popup overlay |
| Persistence | Stays until state changes | Disappears after timeout |
| Use case | Persistent status display | Feedback after actions |
| Defined in | `get_tile()`, modals | Action return value |

**Use Alert when:**

- Status should be visible until resolved
- Displaying errors that block functionality
- Showing warnings about state (low disk, etc.)

**Use Notify when:**

- Confirming action completion
- Showing brief success/failure messages
- User feedback that doesn't need to persist

---

## Combining Feedback Components

```python
from ContaraNAS.core.ui import Stack, Alert, Spinner, Text, Progress

# Loading with progress
loading_state = Stack(
    direction="vertical",
    gap="4",
    align="center",
    children=[
        Spinner(size="lg"),
        Text(content="Downloading update..."),
        Progress(value=45, max=100, label="45%"),
    ],
)

# Error with retry
error_state = Stack(
    direction="vertical",
    gap="4",
    children=[
        Alert(
            title="Connection Failed",
            message="Could not reach the server. Check your network.",
            variant="error",
        ),
        Button(label="Retry", on_click=self.retry_connection),
    ],
)

# Warning with action
warning_state = Stack(
    direction="vertical",
    gap="4",
    children=[
        Alert(
            title="Low Storage",
            message="Only 5 GB remaining. Consider freeing up space.",
            variant="warning",
        ),
        Button(label="Manage Storage", on_click=self.open_storage),
    ],
)
```

## Best Practices

### Do

- **Use semantic variants** — Match variant to meaning (error = red, success = green)
- **Be specific in messages** — "Failed to save: permission denied" not "Error occurred"
- **Show loading for slow operations** — Any operation > 500ms should show feedback
- **Provide recovery options** — Include retry buttons with errors when appropriate

### Don't

- **Don't overuse alerts** — Reserve for important messages
- **Don't leave spinners indefinitely** — Always have timeouts or error states
- **Don't show multiple notifications** — One at a time is usually enough
- **Don't use error variant for warnings** — Errors are for failures, warnings for caution
