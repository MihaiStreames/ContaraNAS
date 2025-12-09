# State Management

Every module can define a **typed state** using Pydantic models. The state system provides:

- **Type safety** — Your state fields are validated at runtime
- **Dirty tracking** — The framework knows when state has changed
- **Commit control** — You decide when changes are pushed to the frontend
- **Serialization** — State is automatically converted to/from JSON

## Defining State

State is defined as an inner class named `State` that inherits from `ModuleState`:

```python
from ContaraNAS.core.module import Module, ModuleState


class MyModule(Module):
    class State(ModuleState):
        # Define your state fields here
        counter: int = 0
        name: str = ""
        items: list[str] = []
        config: dict[str, str] = {}
```

### Supported Field Types

Because `ModuleState` inherits from Pydantic's `BaseModel`, you can use any type that Pydantic supports:

| Type          | Example                     | Notes                  |
|---------------|-----------------------------|------------------------|
| `int`         | `count: int = 0`            | Integer numbers        |
| `float`       | `percentage: float = 0.0`   | Floating point numbers |
| `str`         | `name: str = ""`            | Text strings           |
| `bool`        | `enabled: bool = False`     | True/False values      |
| `list`        | `items: list[str] = []`     | Lists of any type      |
| `dict`        | `data: dict[str, int] = {}` | Dictionaries           |
| `None`        | `value: str \| None = None` | Optional values        |
| Nested models | `config: MyConfig`          | Custom Pydantic models |

### Default Values

Always provide default values for your fields. This ensures the module works even when state hasn't been initialized:

```python
class State(ModuleState):
    # Good: has defaults
    count: int = 0
    name: str = "Unknown"
    items: list[str] = []

    # Avoid: no defaults (will cause errors)
    # count: int
```

!!! warning "Mutable Defaults"
    For mutable types like `list` and `dict`, Pydantic handles them correctly. Each instance gets its own copy. You can safely use `items: list[str] = []`.

## Accessing State

Once you define a `State` class, an instance is automatically created and available as `self._typed_state`:

```python
class MyModule(Module):
    class State(ModuleState):
        counter: int = 0

    async def initialize(self) -> None:
        # Access state
        if self._typed_state:
            print(f"Counter is: {self._typed_state.counter}")

    @action
    async def increment(self) -> None:
        if self._typed_state:
            self._typed_state.counter += 1
```

### Why Check for None?

The `_typed_state` attribute can be `None` if your module doesn't define a `State` class. Always check before accessing:

```python
# Safe pattern
if self._typed_state:
    self._typed_state.counter += 1


# Or use a property for cleaner access
@property
def state(self) -> "MyModule.State":
    """Type-safe state accessor"""
    assert self._typed_state is not None
    return self._typed_state
```

## Modifying State

Simply assign to state fields like normal Python attributes:

```python
@action
async def update_settings(self, name: str, count: int) -> None:
    if self._typed_state:
        self._typed_state.name = name
        self._typed_state.count = count
```

### Validation

Pydantic validates assignments at runtime. If you assign an invalid type, you'll get an error:

```python
class State(ModuleState):
    count: int = 0


# This will raise a ValidationError
self._typed_state.count = "not a number"
```

## Dirty Tracking

The state system tracks whether any fields have changed since the last commit. This is called "dirty tracking".

### How It Works

1. When you modify a field, the state becomes "dirty"
2. You can check if state is dirty with `self._typed_state.is_dirty`
3. When you call `commit()`, the dirty flag is cleared

```python
if self._typed_state:
    print(self._typed_state.is_dirty)  # False

    self._typed_state.counter = 5
    print(self._typed_state.is_dirty)  # True

    self._typed_state.commit()
    print(self._typed_state.is_dirty)  # False
```

### Getting Changes

You can get a dict of only the fields that changed:

```python
if self._typed_state:
    self._typed_state.name = "New Name"
    self._typed_state.count = 42

    changes = self._typed_state.get_changes()
    # changes = {"name": "New Name", "count": 42}
```

This is useful for logging or debugging.

## Committing State

The `commit()` method signals that your state changes should be pushed to the frontend.

```python
@action
async def refresh_data(self) -> None:
    if self._typed_state:
        # Make changes
        self._typed_state.items = await self.fetch_items()
        self._typed_state.last_updated = datetime.now().isoformat()

        # Push to frontend
        self._typed_state.commit()
```

### What Happens on Commit

1. The commit callback is called (set by the framework)
2. An event is emitted on the event bus
3. The StreamManager receives the event
4. The new state is pushed to the frontend via WebSocket
5. The dirty flag is cleared
6. The current state is saved as the "last committed" state

### When to Commit

Call `commit()` when you want the frontend to see your changes. Common patterns:

```python
# After fetching new data
async def refresh(self):
    data = await self.fetch_external_data()
    self._typed_state.data = data
    self._typed_state.commit()


# After processing user input
@action
async def save_settings(self, **settings):
    self._typed_state.settings = settings
    self._typed_state.commit()


# After a background task updates state
async def on_file_changed(self, path: str):
    self._typed_state.files = await self.scan_directory()
    self._typed_state.commit()
```

### Auto-Commit in Actions

Methods decorated with `@action` automatically commit if the state is dirty when the action completes:

```python
@action
async def increment(self) -> None:
    self._typed_state.counter += 1
    # No need to call commit() - it happens automatically
```

See [Actions](actions.md) for more details.

## Serialization

State is automatically serialized to JSON-compatible dicts for transmission to the frontend.

### to_dict()

Get a dict representation of the entire state:

```python
state_dict = self._typed_state.to_dict()
# {"counter": 5, "name": "Test", "items": ["a", "b"]}
```

### from_dict()

Create a state instance from a dict:

```python
state = MyModule.State.from_dict({
    "counter": 5,
    "name": "Test",
    "items": ["a", "b"]
})
```

### Custom Serialization

For complex types, you can override serialization:

```python
from datetime import datetime
from pydantic import field_serializer


class State(ModuleState):
    last_updated: datetime | None = None

    @field_serializer('last_updated')
    def serialize_datetime(self, dt: datetime | None) -> str | None:
        if dt is None:
            return None
        return dt.isoformat()
```

For complete module examples, see the [GitHub repository](https://github.com/MihaiStreames/ContaraNAS).

---

## Complete Example: Disk Monitor State

A practical example showing state for disk/volume monitoring with history tracking:

```python
from datetime import datetime
from ContaraNAS.core.module import Module, ModuleState
from ContaraNAS.core.ui import Tile, Stat, Progress, LineChart, Stack


class DiskModule(Module):
    class State(ModuleState):
        """State for disk and volume monitoring"""

        # Volume information
        volumes: list[dict] = []  # [{path, size, used, free, filesystem}]
        total_capacity: int = 0   # Total bytes across all volumes
        total_used: int = 0       # Total used bytes

        # SMART health
        smart_status: dict[str, str] = {}  # {"/dev/sda": "PASSED", ...}
        temperature: dict[str, int] = {}   # {"/dev/sda": 35, ...}

        # I/O history for graphs (last 60 readings)
        io_read_history: list[float] = []
        io_write_history: list[float] = []
        max_history: int = 60

        # Status
        last_scan: datetime | None = None
        error: str | None = None

        def add_io_reading(self, read_mbps: float, write_mbps: float) -> None:
            """Add I/O reading and trim history"""
            self.io_read_history.append(read_mbps)
            self.io_write_history.append(write_mbps)

            if len(self.io_read_history) > self.max_history:
                self.io_read_history = self.io_read_history[-self.max_history:]
            if len(self.io_write_history) > self.max_history:
                self.io_write_history = self.io_write_history[-self.max_history:]

    def get_tile(self) -> Tile:
        used_percent = (self._typed_state.total_used / self._typed_state.total_capacity * 100
                        if self._typed_state.total_capacity > 0 else 0)

        return Tile(
            icon="hard-drive",
            title="Storage",
            stats=[
                Stat(label="Used", value=f"{used_percent:.1f}%"),
                Stat(label="Volumes", value=len(self._typed_state.volumes)),
            ],
            content=[
                Progress(
                    value=self._typed_state.total_used,
                    max=self._typed_state.total_capacity,
                    label="Total Usage",
                ),
                LineChart(
                    data=self._typed_state.io_read_history,
                    label="Read I/O",
                    color="primary",
                ),
            ],
        )
```

---

## Best Practices

### Do

- **Always provide defaults** for all fields
- **Use type hints** for all fields
- **Call commit()** after making changes in non-action methods
- **Keep state flat** when possible (avoid deep nesting)
- **Use meaningful field names** that describe the data

### Don't

- **Don't store non-serializable objects** (file handles, connections, etc.)
- **Don't forget to check for None** before accessing `_typed_state`
- **Don't commit too frequently** in tight loops (batch changes first)
- **Don't store secrets** in state (it's sent to frontend)

## See Also

- [Actions](actions.md) — How to modify state from user interactions
- [Declarative UI](ui/index.md) — How to display state in the UI
- [Module Lifecycle](lifecycle.md) — When state is created and destroyed
