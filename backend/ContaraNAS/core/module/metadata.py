from typing import Any

import msgspec


class ModuleDependencies(msgspec.Struct, gc=False, frozen=True):
    """Module dependency specification"""

    python: dict[str, str] = msgspec.field(default_factory=dict)
    python_platform: dict[str, list[str]] = msgspec.field(default_factory=dict)
    system: tuple[str, ...] = ()


class ModuleMetadata(msgspec.Struct, gc=False, frozen=True):
    """Module metadata from module.json"""

    id: str
    name: str
    version: str
    author: str
    description: str
    icon: str  # Lucide icon name (e.g., "Gamepad2", "Monitor")
    min_backend_version: str
    platforms: tuple[str, ...]
    dependencies: ModuleDependencies
    source: str  # "builtin" or "community"

    @classmethod
    def from_json(cls, data: dict[str, Any], source: str) -> "ModuleMetadata":
        """Create metadata from module.json"""
        deps_data = data.get("dependencies", {})
        
        dependencies = ModuleDependencies(
            python=deps_data.get("python", {}),
            python_platform=deps_data.get("python_platform", {}),
            system=tuple(deps_data.get("system", [])),
        )

        engine = data.get("engine", {})
        min_version = engine.get("contaranas", "0.0.0").lstrip("^>=<~")

        return cls(
            id=data["name"],
            name=data.get("displayName", data["name"]),
            version=data["version"],
            author=data.get("author", "Unknown"),
            description=data.get("description", ""),
            icon=data.get("icon", "box"),
            min_backend_version=min_version,
            platforms=tuple(data.get("platforms", ["linux", "windows"])),
            dependencies=dependencies,
            source=source,
        )
