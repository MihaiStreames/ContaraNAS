# System Monitor Module

Monitors CPU, memory, and disk usage with real-time updates.

## Features

- CPU usage and temperature monitoring
- Memory usage tracking
- Disk I/O and space monitoring
- History graphs for CPU and memory
- Platform-specific implementations (Linux/Windows)

## Services

| Service | Purpose |
|---------|---------|
| `CPUService` | CPU info, usage, temperature |
| `MemService` | Memory usage, RAM details |
| `DiskService` | Disk space, I/O statistics |
| `SysMonitorMonitoringService` | Periodic data collection |

## State

```python
class State(ModuleState):
    cpu: dict | None = None
    memory: dict | None = None
    disks: list[dict] = []
    cpu_history: list[float] = []
    memory_history: list[float] = []
    disk_history: dict[str, list[float]] = {}
```

## Actions

| Action | Description |
|--------|-------------|
| `refresh` | Manually update all stats |

## Platform Support

Services use factory pattern to select platform-specific implementations:

- **Linux**: Uses `/proc/stat`, `/proc/meminfo`, `dmidecode`
- **Windows**: Uses WMI queries

## System Dependencies

| Dependency | Required | Purpose |
|------------|----------|---------|
| dmidecode | Optional | RAM module details on Linux |

## Files

```
sys_monitor/
├── __init__.py       # SysMonitorModule class
├── constants.py      # Update intervals, history size
├── dto.py            # Data transfer objects
├── services/         # Platform-specific services
│   ├── base.py       # Abstract base classes
│   ├── linux.py      # Linux implementations
│   ├── windows.py    # Windows implementations
│   └── monitoring.py # Async update loop
├── utils.py          # Helper functions
└── views.py          # Tile builder with tabs
```

## Configuration

Default update interval: 2 seconds (configurable via `DEFAULT_MONITOR_UPDATE_INTERVAL`)

History buffer size: 60 readings (configurable via `HISTORY_SIZE`)
