# module.json Reference

Every module requires a `module.json` file in its root directory. This file defines metadata, dependencies, and capabilities that the framework uses to load and manage your module.

## Minimal Example

```json
{
  "name": "my_module",
  "displayName": "My Module",
  "version": "1.0.0",
  "author": "Your Name",
  "description": "A brief description of what your module does",
  "icon": "Wrench",
  "engine": {
    "contaranas": "^0.1.0"
  },
  "platforms": ["linux", "windows", "darwin"]
}
```

## Complete Example

```json
{
  "name": "steam",
  "displayName": "Steam",
  "version": "1.0.0",
  "author": "MihaiStreames",
  "description": "Monitor your Steam game libraries",
  "icon": "Gamepad2",

  "engine": {
    "contaranas": "^0.1.0"
  },

  "platforms": ["linux", "windows"],

  "dependencies": {
    "python": {
      "vdf": "^3.4",
      "watchdog": ">=6.0.0",
      "aiohttp": ">=3.13.2"
    },
    "python_platform": {
      "windows": ["wmi>=1.5.1", "pywin32>=311"]
    },
    "system": ["steam"]
  },

  "capabilities": {
    "websocket": true,
    "dashboard": true,
    "detailPage": false,
    "settings": false
  },

  "category": "gaming",
  "tags": ["steam", "games", "library"],

  "homepage": "https://github.com/example/my-module",
  "repository": "https://github.com/example/my-module",

  "source": "builtin",
  "requires_network": true
}
```

---

## Field Reference

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | `string` | Unique module identifier. Use lowercase with underscores (e.g., `my_module`). Must match the directory name. |
| `displayName` | `string` | Human-readable name shown in the UI (e.g., `"My Module"`). |
| `version` | `string` | Module version using [semantic versioning](https://semver.org/) (e.g., `"1.0.0"`). |
| `author` | `string` | Module author name or organization. |
| `description` | `string` | Brief description (1-2 sentences) of what the module does. |
| `icon` | `string` | [Lucide](https://lucide.dev/icons/) icon name (e.g., `"Monitor"`, `"Gamepad2"`, `"HardDrive"`). |
| `engine.contaranas` | `string` | Minimum ContaraNAS version required. Uses npm-style semver (e.g., `"^0.1.0"`). |
| `platforms` | `string[]` | Supported platforms: `"linux"`, `"windows"`, `"darwin"` (macOS). |

---

### Dependencies

The `dependencies` object declares what your module needs to run:

#### `dependencies.python`

Python packages installed via pip. Keys are package names, values are version specifiers.

```json
"dependencies": {
  "python": {
    "requests": ">=2.28.0",
    "pyyaml": "^6.0"
  }
}
```

**Version specifier formats:**

| Format | Meaning |
|--------|---------|
| `>=2.28.0` | Version 2.28.0 or higher |
| `^6.0` | Compatible with 6.x (6.0.0 to <7.0.0) |
| `~3.4` | Compatible with 3.4.x |
| `==1.2.3` | Exactly version 1.2.3 |

#### `dependencies.python_platform`

Platform-specific Python packages. Only installed on the specified platform.

```json
"dependencies": {
  "python_platform": {
    "windows": ["wmi>=1.5.1", "pywin32>=311"],
    "linux": ["python-xlib>=0.33"]
  }
}
```

#### `dependencies.system`

System-level dependencies (executables or services that must be present).

```json
"dependencies": {
  "system": ["docker", "ffmpeg"]
}
```

!!! note "System Dependencies"
    System dependencies are checked for availability but **not** automatically installed. The framework will warn users if a required system dependency is missing.

---

### Capabilities

The `capabilities` object declares what features your module uses:

```json
"capabilities": {
  "websocket": true,
  "dashboard": true,
  "detailPage": false,
  "settings": false
}
```

| Capability | Type | Description |
|------------|------|-------------|
| `websocket` | `bool` | Module uses WebSocket for real-time updates |
| `dashboard` | `bool` | Module provides a dashboard tile |
| `detailPage` | `bool` | Module has a dedicated detail page |
| `settings` | `bool` | Module has configurable settings |

---

### Metadata Fields

| Field | Type | Description |
|-------|------|-------------|
| `category` | `string` | Module category for organization (e.g., `"monitoring"`, `"gaming"`, `"media"`, `"utilities"`) |
| `tags` | `string[]` | Searchable tags for discovery |
| `homepage` | `string` | URL to project homepage or documentation |
| `repository` | `string` | URL to source code repository |

---

### Runtime Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `source` | `string` | — | `"builtin"` for core modules, `"community"` for user-installed modules. Set automatically by the loader. |
| `requires_network` | `bool` | `false` | Whether the module requires network access to function |

---

## Validation

The framework validates `module.json` when loading modules. Common validation errors:

| Error | Cause |
|-------|-------|
| `Missing required field: name` | A required field is missing |
| `Invalid version format` | Version doesn't follow semver |
| `Unknown platform` | Platform not in `linux`, `windows`, `darwin` |
| `Module name mismatch` | `name` doesn't match directory name |

---

## Best Practices

### Naming

- Use `snake_case` for the `name` field
- Use Title Case for `displayName`
- Keep names concise but descriptive

```json
{
  "name": "docker_manager",
  "displayName": "Docker Manager"
}
```

### Versioning

Follow semantic versioning:

- **MAJOR** (1.x.x): Breaking changes
- **MINOR** (x.1.x): New features, backwards compatible
- **PATCH** (x.x.1): Bug fixes

### Dependencies

- Specify minimum versions, not exact versions
- Use `^` for packages that follow semver
- Use `>=` when you need a specific feature

```json
"python": {
  "requests": "^2.28",
  "some-unstable-lib": ">=1.2.3,<2.0"
}
```

### Platform Support

Only list platforms you've actually tested:

```json
"platforms": ["linux", "windows"]
```

!!! warning "Don't Guess"
    Don't include `darwin` unless you've tested on macOS. Platform-specific code often has subtle differences.

---

## See Also

- [Module Development Overview](index.md) — Getting started with modules
- [Module Lifecycle](lifecycle.md) — How modules are initialized and managed
- [Publishing](publishing.md) — Publishing community modules
