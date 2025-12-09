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

### For the Curious

Want to understand how ContaraNAS works under the hood?

→ **[Internals](internals/index.md)** — Render pipeline, server-driven UI, type generation

## License

MIT — [See LICENSE](https://github.com/MihaiStreames/ContaraNAS/blob/main/LICENSE)
