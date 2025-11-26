# ContaraNAS Marketplace

Module marketplace server for ContaraNAS community modules.

## Running

```bash
cd marketplace
uv sync
uv run uvicorn server:app --port 8001 --reload
```

## API Endpoints

| Endpoint                                        | Description                  |
|-------------------------------------------------|------------------------------|
| `GET /registry?backend_version=x.x.x`           | Get filtered module registry |
| `GET /modules/{id}?backend_version=x.x.x`       | Get module details           |
| `GET /modules/{id}/versions/{version}/download` | Download module zip          |
| `GET /modules/{id}/icon`                        | Get module icon              |
| `GET /health`                                   | Health check                 |

## Adding Modules

1. Create folder in `data/modules/{module-name}/`
2. Add `{version}.zip` file
3. Optionally add `icon.png`
4. Update `data/registry.json`

## Registry Format

```json
{
	"schema_version": 1,
	"modules": {
		"example-module": {
			"display_name": "Example Module",
			"short_description": "Short description here",
			"description": "Full description here",
			"author": "Author Name",
			"license": "MIT",
			"repository": "https://github.com/...",
			"category": "utilities",
			"tags": [
				"example",
				"demo"
			],
			"has_icon": true,
			"versions": {
				"1.0.0": {
					"min_backend_version": "0.1.0",
					"platforms": [
						"linux",
						"windows"
					],
					"changelog": "Initial release",
					"published_at": "2025-01-15T10:00:00Z",
					"size_bytes": 12345,
					"dependencies": {
						"python": {
							"requests": ">=2.28.0"
						},
						"system": []
					}
				}
			}
		}
	}
}
```