# Module Development

This section covers everything you need to know to build modules for ContaraNAS.

## Overview

ContaraNAS uses a **modular architecture** where functionality is provided through independent modules. Each module is a self-contained Python package that:

- Defines its own **state** (data it manages)
- Provides a **tile** for the dashboard (how it appears to users)
- Exposes **actions** (things users can do)
- Optionally provides **modals** (detailed views and forms)

The framework handles all the complexity of:

- Rendering your UI on the frontend
- Synchronizing state between backend and frontend
- Routing user interactions back to your code
- Managing module lifecycle (enable, disable, initialize)

**You write Python. The framework does the rest.**

## Module Types

### Built-in Modules

Located in `backend/ContaraNAS/modules/builtin/`. These ship with ContaraNAS and are maintained by the core team.

### Community Modules

Located in `backend/ContaraNAS/modules/community/`. These are installed by users and can be developed by anyone.

## Directory Structure

A module is a directory containing at minimum:

```
my_module/
├── __init__.py      # Module class (required)
└── module.json      # Module metadata (required)
```

A more complete module might look like:

```
my_module/
├── __init__.py          # Module class
├── module.json          # Metadata
├── controllers/         # Business logic
│   ├── __init__.py
│   └── main_controller.py
├── services/            # External integrations
│   ├── __init__.py
│   └── api_service.py
└── dtos/                # Data transfer objects
    ├── __init__.py
    └── models.py
```

## Quick Start

Here is a minimal working module:

```python
# my_module/__init__.py

from ContaraNAS.core.module import Module, ModuleState
from ContaraNAS.core.action import action

class MyModule(Module):
    """A simple example module"""

    class State(ModuleState):
        counter: int = 0

    async def initialize(self) -> None:
        """Called once when the module is first enabled"""
        pass

    async def start_monitoring(self) -> None:
        """Called when module is enabled (start background tasks here)"""
        pass

    async def stop_monitoring(self) -> None:
        """Called when module is disabled (clean up here)"""
        pass

    def get_tile(self) -> "Tile":
        """Return the dashboard tile UI"""
        from ContaraNAS.core.ui import Tile, Stat, Button
        return Tile(
            icon="counter",
            title="My Module",
            stats=[Stat(label="Count", value=self._typed_state.counter if self._typed_state else 0)],
            actions=[Button(label="Increment", on_click=self.increment)],
        )

    @action
    async def increment(self) -> None:
        """Increment the counter (called from frontend)"""
        if self._typed_state:
            self._typed_state.counter += 1
            self._typed_state.commit()
```

```json
// my_module/module.json
{
  "name": "my_module",
  "displayName": "My Module",
  "version": "1.0.0",
  "author": "Your Name",
  "description": "A simple example module",
  "icon": "wrench",
  "engine": {
    "contaranas": "^0.1.0"
  },
  "platforms": ["linux", "windows", "darwin"],
  "dependencies": {}
}
```

!!! note "Icon Names"
    The `icon` field uses [Lucide](https://lucide.dev/icons/) icon names (e.g., `"wrench"`, `"gamepad-2"`, `"hard-drive"`). Browse available icons at [lucide.dev/icons](https://lucide.dev/icons/).

## What to Read Next

1. **[State Management](state.md)** — How to define and manage module state
2. **[Declarative UI](ui/index.md)** — How to build your module's interface
3. **[Actions](actions.md)** — How to handle user interactions
4. **[Module Lifecycle](lifecycle.md)** — Initialize, enable, disable, cleanup

## Key Concepts

| Concept | Description |
|---------|-------------|
| **ModuleState** | A Pydantic model that holds your module's data. Changes are tracked automatically. |
| **Component** | A UI building block (Button, Card, Table, etc.) defined in Python, rendered in frontend. |
| **Action** | A method decorated with `@action` that can be called from the frontend. |
| **Tile** | The card shown on the dashboard representing your module. |
| **Modal** | A popup dialog for detailed views or forms. |
| **commit()** | Signals that state changes should be pushed to the frontend. |
