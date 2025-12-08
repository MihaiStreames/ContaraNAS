# ContaraNAS

A modular desktop application for monitoring and managing NAS systems at home.

## Features

- **Steam Library Monitor** - Track game installations and library sizes
- **System Monitor** - Real-time CPU, memory, and disk monitoring
- **Real-time Updates** - WebSocket-based live data streaming
- **Modular Architecture** - Enable/disable features as needed
- **Marketplace** - Community modules (coming soon)

## Quick Start

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

## Requirements

- Python 3.13+
- Node.js 18+ / pnpm
- Rust (for Tauri)

## License

MIT - [See LICENSE](LICENSE)
