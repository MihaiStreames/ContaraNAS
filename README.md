# ContaraNAS

A modular desktop application for monitoring and managing NAS systems at home.

## Features

- 🎮 **Steam Library Monitor** - Track game installations and library sizes
- 💻 **System Monitor** - Real-time CPU, memory, and disk monitoring
- 🔄 **Real-time Updates** - WebSocket-based live data streaming
- 🧩 **Modular Architecture** - Enable/disable features as needed
- 🛒 **Marketplace** - Community modules (coming soon)

## Project Structure

```
ContaraNAS/
├── backend/         # FastAPI server
├── frontend/        # Tauri + SvelteKit app
└── marketplace/     # Module marketplace server
```

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

### Marketplace

```bash
cd marketplace
uv sync
uv run uvicorn server:app --port 8001
```

## Requirements

- Python 3.13+
- Node.js 18+ / pnpm
- Rust (for Tauri)

## License

MIT - [See LICENSE](LICENSE)