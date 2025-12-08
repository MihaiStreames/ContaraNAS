# ContaraNAS Backend

FastAPI server for system monitoring and module management.

## Setup

```bash
uv sync
```

## Running

```bash
# Default (0.0.0.0:8000)
uv run -m ContaraNAS

# Custom options
uv run -m ContaraNAS --port 8080 --reload

# Help
uv run -m ContaraNAS --help
```

## API Endpoints

| Endpoint                           | Description           |
|------------------------------------|-----------------------|
| `GET /health`                      | Health check          |
| `GET /info`                        | Server info           |
| `GET /api/modules`                 | List modules          |
| `POST /api/modules/{name}/enable`  | Enable module         |
| `POST /api/modules/{name}/disable` | Disable module        |
| `WS /ws`                           | Real-time data stream |

## Modules

Builtin modules in `ContaraNAS/modules/builtin/`:

- **steam** - Steam library monitoring
- **sys_monitor** - System resource monitoring

Community modules installed to `ContaraNAS/modules/community/`.

## Module Development

See the [Module Development documentation](https://contaranas.xyz/modules/) for:

- Creating custom modules
- State management with `ModuleState`
- Declarative UI components
- Action handling

## System Dependencies

| Module      | Dependency        | Required                          |
|-------------|-------------------|-----------------------------------|
| steam       | Steam client      | Optional (empty data if missing)  |
| sys_monitor | dmidecode (Linux) | Optional (RAM details if missing) |
