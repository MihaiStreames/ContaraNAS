from dataclasses import dataclass, field
from typing import Any


@dataclass
class ModuleDependencies:
    """Module dependency specification"""

    python: dict[str, str] = field(default_factory=dict)
    python_platform: dict[str, list[str]] = field(default_factory=dict)
    system: list[str] = field(default_factory=list)


@dataclass
class ModuleMetadata:
    """Module metadata from module.json"""

    # Identity
    id: str
    name: str
    version: str
    author: str
    description: str

    # Requirements
    min_backend_version: str
    platforms: list[str]

    # Dependencies
    dependencies: ModuleDependencies

    # Source
    source: str  # "builtin" or "community"

    @classmethod
    def from_json(cls, data: dict[str, Any], source: str) -> "ModuleMetadata":
        """Create metadata from module.json"""
        deps_data = data.get("dependencies", {})

        python_deps = deps_data.get("python", {})
        python_platform = deps_data.get("python_platform", {})
        system_deps = deps_data.get("system", [])

        dependencies = ModuleDependencies(
            python=python_deps,
            python_platform=python_platform,
            system=system_deps,
        )

        # Parse min_backend_version from engine field
        engine = data.get("engine", {})
        min_version = engine.get("contaranas", "0.0.0")
        # Strip ^ or >= prefix if present
        min_version = min_version.lstrip("^>=<~")

        return cls(
            id=data["name"],
            name=data.get("displayName", data["name"]),
            version=data["version"],
            author=data.get("author", "Unknown"),
            description=data.get("description", ""),
            min_backend_version=min_version,
            platforms=data.get("platforms", ["linux", "windows"]),
            dependencies=dependencies,
            source=source,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "author": self.author,
            "description": self.description,
            "min_backend_version": self.min_backend_version,
            "platforms": self.platforms,
            "dependencies": {
                "python": self.dependencies.python,
                "python_platform": self.dependencies.python_platform,
                "system": self.dependencies.system,
            },
            "source": self.source,
        }
