# ContaraNAS

A modular desktop application for monitoring and managing NAS systems at home.

## Features

- **Steam Library Monitor** - Track game installations and library sizes
- **System Monitor** - Real-time CPU, memory, and disk monitoring
- **Real-time Updates** - WebSocket-based live data streaming
- **Modular Architecture** - Enable/disable features as needed
- **Marketplace** - Community modules (coming soon)

## Documentation

Full documentation available at [contaranas.xyz](https://contaranas.xyz/) (or run `mkdocs serve` in `/docs`).

### For Module Developers

- [Module Development](https://contaranas.xyz/modules/) - Overview and getting started
- [State Management](https://contaranas.xyz/modules/state/) - Typed state with dirty tracking
- [Declarative UI](https://contaranas.xyz/modules/ui/) - Build UIs in Python
- [Actions](https://contaranas.xyz/modules/actions/) - Handle user interactions

## Development Setup

### Backend

```bash
cd backend
uv sync
uv run -m ContaraNAS
```

### Frontend

```bash
cd frontend
pnpm install
pnpm tauri dev
```

### Requirements

- Python 3.13+
- Node.js 18+ / pnpm
- Rust (for Tauri)

## License

MIT - [See LICENSE](LICENSE)
