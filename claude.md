# Claude Development Guidelines for ContaraNAS

## Project Overview

- **Language**: Python (100% Python codebase)
- **Architecture**: MVVM (Model-View-ViewModel) pattern
- **UI Framework**: NiceGUI for native interface

## MVVM Architecture

### Understanding the MVVM Pattern in ContaraNAS

```
┌─────────────────────────────────────────────────────────┐
│                      Module Layer                       │
│  - SteamModule, etc.                                    │
│  - Manages lifecycle (enable/disable/initialize)        │
│  - Contains reference to Controller                     │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                    Controller Layer                     │
│  - SteamController, etc.                                │
│  - Business logic and data operations                   │
│  - Interacts with Services                              │
│  - Provides methods for Tiles to call                   │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                   ViewModel Layer                       │
│  - BaseTileViewModel (dataclass)                        │
│  - Pure data objects for UI display                     │
│  - No business logic                                    │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                      View Layer                         │
│  - SteamTile, SystemMonitorTile, etc.                   │
│  - Renders UI using NiceGUI                             │
│  - Delegates to helper functions for rendering          │
│  - Calls Controller methods for data/actions            │
└─────────────────────────────────────────────────────────┘
```

### Accessing Module Controllers from Tiles

Tiles receive a `DashboardController` that provides access to module controllers:

```python
# In a tile, access the module-specific controller like this:
steam_controller = self.controller.get_module_controller("steam")
games = await steam_controller.get_library_games(library_path)
```

## Code Organization Principles

### 1. Code Splitting

- **Always split code into smaller, manageable modules**
- Break down large components into smaller, focused sub-components
- Extract reusable logic into utility/helper functions
- Separate business logic (Controller/Service) from presentation logic (Tile/Helper)
- Keep files under 300 lines when possible

### 2. Constants Management

- **Use constants across the app for each module**
- Define module-specific constants in dedicated constant files (e.g., `steam/constants.py`)
- Group related constants together with clear comments
- Use uppercase for constant names (e.g., `SORT_BY_SIZE`, `HTTP_TIMEOUT`)
- Avoid magic numbers and strings - always use named constants

### 3. Codebase Cleanliness

- Maintain consistent code structure across modules
- Remove unused imports, variables, and code
- Follow established patterns in the codebase
- Keep components focused on a single responsibility (Single Responsibility Principle)
- Use descriptive names for variables, functions, and classes

## File Structure Best Practices

```
modules/
└── module_name/
    ├── __init__.py          # Module class
    ├── constants.py         # Module constants
    ├── controllers/         # Business logic
    ├── services/            # External operations (API, file I/O)
    ├── dtos/                # Data transfer objects
    └── utils/               # Helper functions

gui/
├── components/
│   └── module_name/
│       ├── module_tile.py           # Main tile view
│       └── module_tile_helper.py    # Rendering helpers
└── controllers/
    └── dashboard_controller.py      # GUI command handler
```

## Example Constant Organization

```python
# steam/constants.py
"""Steam module constants"""

# Image service constants
MIN_VALID_IMAGE_SIZE = 1000  # Minimum bytes for a valid image file
IMAGE_DOWNLOAD_DELAY = 0.1   # Seconds between downloads

# Game library modal constants
SORT_BY_SIZE = "size"
SORT_BY_NAME = "name"
SORT_BY_LAST_PLAYED = "last_played"

SORT_OPTIONS = {
    SORT_BY_SIZE: "Size",
    SORT_BY_NAME: "Name",
    SORT_BY_LAST_PLAYED: "Last Played"
}
```

## General Guidelines

- Follow MVVM pattern strictly - no business logic in Views/Tiles
- Use Python type hints consistently
- Write self-documenting code with clear naming
- Extract complex logic into well-named helper functions
- Keep the UI layer thin - delegate rendering to helper functions
- Delegate data operations to Controllers and Services
- Use async/await for I/O operations
- Prefer composition over inheritance
