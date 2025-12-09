# Feedback Components

Feedback components communicate status, progress, and system messages to users.

## Alert

Displays a message with semantic meaning.

```python
from ContaraNAS.core.ui import Alert

Alert(message="Your library is being scanned.", variant="info")
Alert(message="Settings saved!", variant="success")
Alert(message="Disk space is running low.", variant="warning", title="Warning")
Alert(message="Failed to connect.", variant="error", title="Error")
```

### Props

| Prop      | Type                                          | Default  | Description              |
|-----------|-----------------------------------------------|----------|--------------------------|
| `message` | `str`                                         | Required | Alert message text       |
| `variant` | `"info"`, `"success"`, `"warning"`, `"error"` | `"info"` | Visual style and meaning |
| `title`   | `str` or `None`                               | `None`   | Optional title/heading   |

### Variants

| Variant     | Use Case                             | Color         |
|-------------|--------------------------------------|---------------|
| `"info"`    | General information, tips            | Blue          |
| `"success"` | Completed actions, positive feedback | Green         |
| `"warning"` | Caution, non-critical issues         | Yellow/Orange |
| `"error"`   | Errors, failures, critical issues    | Red           |

---

## Spinner

A loading indicator for async operations.

```python
from ContaraNAS.core.ui import Spinner

Spinner()
Spinner(label="Loading...")
Spinner(size="lg")
```

### Props

| Prop    | Type                   | Default | Description              |
|---------|------------------------|---------|--------------------------|
| `size`  | `"sm"`, `"md"`, `"lg"` | `"md"`  | Spinner size             |
| `label` | `str` or `None`        | `None`  | Text shown below spinner |

### Sizes

| Size   | Use Case                   |
|--------|----------------------------|
| `"sm"` | Inline loading, buttons    |
| `"md"` | General loading states     |
| `"lg"` | Full-page or modal loading |

---

## Alert vs Notify

`Alert` is a UI component. `Notify` is an action result (see [Actions](../actions.md#notify)).

| Feature     | Alert (Component)         | Notify (Action Result)   |
|-------------|---------------------------|--------------------------|
| Location    | Embedded in UI            | Toast/popup overlay      |
| Persistence | Stays until state changes | Disappears after timeout |
| Use case    | Persistent status display | Feedback after actions   |

- **Alert** — Persistent status, errors that block functionality, warnings
- **Notify** — Action completion feedback, brief success/failure messages

## Best Practices

- Use semantic variants — match variant to meaning
- Be specific in messages — "Failed to save: permission denied" not "Error occurred"
- Show loading for operations > 500ms
- Provide recovery options (retry buttons) with errors
