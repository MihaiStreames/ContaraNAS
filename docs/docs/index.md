# ContaraNAS

!!! warning "Early Development"
    ContaraNAS is under active development. APIs may change.

A modular desktop application for monitoring and managing NAS systems.

## What is ContaraNAS?

ContaraNAS connects your desktop to your NAS, providing real-time monitoring through a plugin-based module system.
Built-in modules track Steam libraries, system resources, and more. Community modules extend functionality further.

**Core features:**

- **Modular design** — Enable/disable features as needed
- **Real-time monitoring** — WebSocket-based live updates
- **Community marketplace** — Install third-party modules
- **Cross-platform** — Tauri-based desktop app

## Documentation

### For Module Developers

Build your own modules to extend ContaraNAS:

- **[Module Development](modules/index.md)** — Overview and getting started
- **[State Management](modules/state.md)** — Typed state with dirty tracking
- **[Declarative UI](modules/ui/index.md)** — Build UIs in Python
- **[Actions](modules/actions.md)** — Handle user interactions

## Development Setup

```bash
# Backend
cd backend
uv sync
uv run -m ContaraNAS

# Frontend
cd frontend
pnpm install
pnpm tauri dev
```

The backend runs on `localhost:8000`. The frontend will open automatically and prompt for pairing.

### Requirements

| Component | Version            |
|-----------|--------------------|
| Python    | 3.13+              |
| Node.js   | 18+                |
| pnpm      | Latest             |
| Rust      | Latest (for Tauri) |

## License

MIT — [See LICENSE](https://github.com/MihaiStreames/ContaraNAS/blob/main/LICENSE)
