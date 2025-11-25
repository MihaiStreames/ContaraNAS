from dataclasses import dataclass
from typing import Any


@dataclass
class ModuleDependencies:
    """Module dependency specification"""

    python_packages: dict[str, str]  # package: version_spec
    platform_specific: dict[str, list[str]]  # platform: [packages]
    system_packages: list[str]  # System-level packages (apt, brew, etc)


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
        backend_deps = data.get("backend", {}).get("dependencies", {})
        platform_deps = data.get("backend", {}).get("platform_dependencies", {})
        system_deps = data.get("system_deps", [])

        dependencies = ModuleDependencies(
            python_packages=backend_deps,
            platform_specific=platform_deps,
            system_packages=system_deps
        )

        return cls(
            id=data["name"],
            name=data.get("displayName", data["name"]),
            version=data["version"],
            author=data["author"],
            description=data["description"],
            min_backend_version=data.get("engine", {}).get("contaranas", "0.0.0"),
            platforms=data.get("platforms", ["linux", "windows"]),
            dependencies=dependencies,
            source=source
        )
