# ContaraNAS

A modular desktop application for monitoring and managing NAS systems at home.

## Features

- 🎮 **Steam Library Monitor**: Track game installations, library sizes, and drive usage across multiple Steam libraries
- 💻 **System Monitor**: Real-time CPU, memory, and disk monitoring with per-core visualization
- 🔄 **Real-time Updates**: WebSocket-based streaming for live data updates
- 🖥️ **Native Desktop App**: Tauri + SvelteKit frontend with FastAPI backend

## Quick Start

### Backend

```bash
# Clone the repository
git clone https://github.com/MihaiStreames/ContaraNAS
cd ContaraNAS

# Install dependencies
uv sync 

# If NAS is running on Windows
uv sync --extra windows

# Run the API server
uv run -m ContaraNAS.main
```

### Frontend

```bash
cd frontend

# Install dependencies
pnpm install

# Run in development mode
pnpm tauri dev
```

### Requirements

- Python 3.13+
- Node.js 18+ / pnpm
- Rust (for Tauri)
- Steam installed (for Steam module)
- **Linux**: `dmidecode` installed (for hardware monitoring)
- **Windows**: Administrative privileges may be required for hardware monitoring