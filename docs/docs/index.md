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

Build your own modules to extend ContaraNAS. Start here:

→ **[Getting Started](modules/index.md)** — Module structure, quick start example, key concepts

Then explore:

- [State](modules/state.md) — Typed state with dirty tracking
- [Actions](modules/actions.md) — Handle user interactions
- [UI Components](modules/ui/index.md) — Build UIs in Python
- [Lifecycle](modules/lifecycle.md) — Module initialization and monitoring

<!-- TODO: Uncomment when internals section is created
### For the Curious

Want to understand how ContaraNAS works under the hood?

→ **[Internals](internals/index.md)** — Render pipeline, WebSocket protocol, type generation
-->

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

### Type Generation

TypeScript types are auto-generated from Python Pydantic models via OpenAPI:

```bash
cd frontend
pnpm run generate
```

This generates:

- `src/lib/api/types.generated.ts` — Full OpenAPI types
- `src/lib/api/ui.ts` — UI component types (`TileSchema`, `ButtonSchema`, etc.)
- `src/lib/api/responses.ts` — API response types (`AppStateResponse`, etc.)

Run this after modifying backend schemas in `backend/ContaraNAS/api/schemas/`.

### Requirements

| Component | Version            |
|-----------|--------------------|
| Python    | 3.13+              |
| Node.js   | 18+                |
| pnpm      | Latest             |
| Rust      | Latest (for Tauri) |

## License

MIT — [See LICENSE](https://github.com/MihaiStreames/ContaraNAS/blob/main/LICENSE)
