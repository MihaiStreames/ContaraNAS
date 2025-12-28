<a id="contributing-top"></a>

<!-- HEADER -->
<br />
<div align="center">
  <h1>Contributing to ContaraNAS</h1>
  <p>Thank you for your interest in contributing to ContaraNAS!</p>
</div>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#development-setup">Development Setup</a>
      <ul>
        <li><a href="#requirements">Requirements</a></li>
        <li><a href="#installation">Installation</a></li>
        <li><a href="#running-locally">Running Locally</a></li>
      </ul>
    </li>
    <li><a href="#type-generation">Type Generation</a></li>
    <li><a href="#code-style">Code Style</a></li>
    <li><a href="#project-structure">Project Structure</a></li>
    <li><a href="#making-changes">Making Changes</a></li>
    <li><a href="#testing">Testing</a></li>
    <li><a href="#pull-requests">Pull Requests</a></li>
    <li><a href="#documentation">Documentation</a></li>
  </ol>
</details>

<!-- DEVELOPMENT SETUP -->
## Development Setup

### Requirements

| Tool | Version | Notes |
|------|---------|-------|
| Python | 3.13+ | |
| Node.js | 18+ | |
| pnpm | Latest | Package manager for frontend |
| Rust | Latest | Required for Tauri |
| uv | Latest | Python package manager |

<p align="right">(<a href="#contributing-top">back to top</a>)</p>

### Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/MihaiStreames/ContaraNAS.git
cd ContaraNAS
```

**Backend:**

```bash
cd backend
uv sync
```

**Frontend:**

```bash
cd frontend
pnpm install
```

<p align="right">(<a href="#contributing-top">back to top</a>)</p>

### Running Locally

Start both the backend and frontend in separate terminals:

```bash
# Terminal 1: Backend
cd backend
uv run -m ContaraNAS

# Terminal 2: Frontend (Tauri dev mode)
cd frontend
pnpm tauri dev
```

The backend runs on `http://localhost:8000`. The frontend connects via WebSocket.

<p align="right">(<a href="#contributing-top">back to top</a>)</p>

<!-- TYPE GENERATION -->
## Type Generation

After changing Python schemas or components, regenerate TypeScript types:

```bash
./scripts/generate-types.sh
```

This script:

1. Exports FastAPI's OpenAPI schema
2. Generates TypeScript type aliases
3. Runs `openapi-typescript` to create `types.generated.ts`
4. Verifies compilation

<p align="right">(<a href="#contributing-top">back to top</a>)</p>

<!-- CODE STYLE -->
## Code Style

### Python

We use [Ruff](https://docs.astral.sh/ruff/) for linting and formatting:

```bash
cd backend
uv run ruff check .
uv run ruff format .
```

Key conventions:

* Line length: 100
* Double quotes
* Google-style docstrings
* Type hints encouraged

### TypeScript/Svelte

Standard Svelte/TypeScript conventions. Run type checking:

```bash
cd frontend
pnpm check
```

<p align="right">(<a href="#contributing-top">back to top</a>)</p>

<!-- PROJECT STRUCTURE -->
## Project Structure

```
ContaraNAS/
├── backend/
│   ├── ContaraNAS/
│   │   ├── api/           # FastAPI routes, WebSocket, schemas
│   │   ├── core/          # Module system, UI components, auth
│   │   ├── modules/       # Built-in and community modules
│   │   └── main.py        # Entry point
│   ├── tests/
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── lib/           # Components, API client, stores
│   │   └── routes/        # SvelteKit pages
│   ├── src-tauri/         # Tauri (Rust) configuration
│   └── package.json
├── scripts/               # Build and generation scripts
└── docs/                  # MkDocs documentation
```

<p align="right">(<a href="#contributing-top">back to top</a>)</p>

<!-- MAKING CHANGES -->
## Making Changes

### Adding a UI Component

1. Create the runtime component in `backend/ContaraNAS/core/ui/`
2. Create the schema in `backend/ContaraNAS/api/schemas/components.py`
3. Add to the `ComponentSchema` union in `api/schemas/ui.py`
4. **Write a pytest** in `backend/tests/` demonstrating how the component works
5. Run `./scripts/generate-types.sh`
6. Implement the Svelte component in `frontend/src/lib/components/`

Every new component requires a test. The test serves as living documentation showing how the component is constructed and serialized.

### Modifying the API

1. Update routes in `backend/ContaraNAS/api/routes/`
2. Update schemas in `backend/ContaraNAS/api/schemas/`
3. Regenerate types: `./scripts/generate-types.sh`

<p align="right">(<a href="#contributing-top">back to top</a>)</p>

<!-- TESTING -->
## Testing

Run the test suite:

```bash
cd backend
uv run pytest
```

Tests live in `backend/tests/`. We use pytest with async support.

<p align="right">(<a href="#contributing-top">back to top</a>)</p>

<!-- PULL REQUESTS -->
## Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Make your changes
4. Run linting and tests
5. Submit a PR against `main`

Keep PRs focused. One feature or fix per PR.

<p align="right">(<a href="#contributing-top">back to top</a>)</p>

<!-- DOCUMENTATION -->
## Documentation

Docs are built with MkDocs. To work on documentation:

1. **Install MkDocs and dependencies**

   ```bash
   cd docs
   pip install mkdocs-material
   ```

2. **Serve locally**

   ```bash
   mkdocs serve
   ```

   Preview at `http://localhost:8000`

3. **Build static site**

   ```bash
   mkdocs build
   ```

<p align="right">(<a href="#contributing-top">back to top</a>)</p>

---

<div align="center">
  <p>Questions? Open an issue at <a href="https://github.com/MihaiStreames/ContaraNAS/issues">github.com/MihaiStreames/ContaraNAS/issues</a></p>
</div>
