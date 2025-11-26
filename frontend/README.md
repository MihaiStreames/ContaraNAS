# ContaraNAS Frontend

Tauri + SvelteKit desktop application.

## Setup

```bash
pnpm install
```

## Development

```bash
pnpm tauri dev
```

## Build

```bash
pnpm tauri build
```

## Structure

```
src/
├── lib/
│   ├── api/          # HTTP client
│   ├── components/   # UI components
│   ├── stores/       # Svelte stores
│   └── websocket/    # WebSocket client
└── routes/           # Pages
```

## Configuration

Backend URL configured in `src/lib/api/config.ts`:

```typescript
export const API_CONFIG = {
	baseUrl: 'http://localhost:8000',
	wsUrl: 'ws://localhost:8000/ws',
};
```