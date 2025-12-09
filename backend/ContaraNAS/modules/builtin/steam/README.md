# Steam Module

Monitors Steam game libraries and displays installed games.

## Features

- Auto-detects Steam installation path
- Scans all Steam library folders
- Real-time monitoring for game installs/uninstalls
- Displays game sizes, shader caches, and workshop content
- Downloads game header images from Steam CDN

## Services

| Service | Purpose |
|---------|---------|
| `SteamLibraryService` | Find Steam path and library folders |
| `SteamCacheService` | Cache manifest data for quick access |
| `SteamGameLoaderService` | Parse ACF manifests into game objects |
| `SteamImageService` | Download and cache game header images |
| `SteamMonitoringService` | Watch for manifest file changes |
| `SteamParsingService` | Parse VDF and ACF file formats |

## State

```python
class State(ModuleState):
    steam_available: bool = False
    steam_path: str | None = None
    libraries: list[dict] = []
    games: list[dict] = []
    total_games: int = 0
    total_libraries: int = 0
    total_size: int = 0
```

## Actions

| Action | Description |
|--------|-------------|
| `refresh` | Manually rescan all libraries |
| `open_library(library_path)` | Open modal for specific library |

## Platform Support

- **Linux**: `~/.steam/steam`, `~/.local/share/Steam`
- **Windows**: `C:\Program Files (x86)\Steam`

## Files

```
steam/
├── __init__.py       # SteamModule class
├── dto.py            # Data transfer objects (SteamGame, etc.)
├── services/         # Service implementations
│   ├── cache.py      # Manifest cache
│   ├── game_loader.py
│   ├── image.py      # Image downloading
│   ├── library.py    # Library discovery
│   ├── manifest.py   # Manifest parsing
│   ├── monitoring.py # File watching
│   ├── parsing.py    # VDF/ACF parsing
│   └── path.py       # Path utilities
├── utils.py          # Helper functions
└── views.py          # Tile and modal builders
```
