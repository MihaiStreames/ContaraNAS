from dataclasses import dataclass, field
from typing import Any

from .category import ModuleCategory
from .source import ModuleSource


@dataclass
class ModuleMetadata:
    """Module metadata loaded from module.json"""

    # Basic info
    version: str = "0.0.0"
    author: str = "Unknown"
    description: str = ""
    long_description: str = ""

    # Categorization
    category: ModuleCategory = ModuleCategory.OTHER
    tags: list[str] = field(default_factory=list)

    # Links
    homepage: str = ""
    repository: str = ""
    documentation: str = ""

    # Visual
    icon: str = ""

    # Dependencies
    dependencies: list[str] = field(default_factory=list)  # Other modules
    python_deps: list[str] = field(default_factory=list)  # pip packages
    system_deps: list[str] = field(default_factory=list)  # System packages

    # Compatibility
    min_backend_version: str = "0.1.0"
    max_backend_version: str | None = None
    supported_platforms: list[str] = field(default_factory=lambda: ["linux", "windows"])

    # Source
    source: ModuleSource = ModuleSource.BUILTIN

    # Requirements
    requires_root: bool = False
    requires_network: bool = False
    requires_docker: bool = False

    @classmethod
    def from_dict(cls, data: dict) -> "ModuleMetadata":
        """Create metadata from dictionary (loaded from JSON)"""
        # Handle category enum
        category_str = data.get("category", "other")
        try:
            category = ModuleCategory(category_str)
        except ValueError:
            category = ModuleCategory.OTHER

        # Handle source enum
        source_str = data.get("source", "builtin")
        try:
            source = ModuleSource(source_str)
        except ValueError:
            source = ModuleSource.BUILTIN

        return cls(
            version=data.get("version", "0.0.0"),
            author=data.get("author", "Unknown"),
            description=data.get("description", ""),
            long_description=data.get("long_description", ""),
            category=category,
            tags=data.get("tags", []),
            homepage=data.get("homepage", ""),
            repository=data.get("repository", ""),
            documentation=data.get("documentation", ""),
            icon=data.get("icon", ""),
            dependencies=data.get("dependencies", []),
            python_deps=data.get("python_deps", []),
            system_deps=data.get("system_deps", []),
            min_backend_version=data.get("min_backend_version", "0.1.0"),
            max_backend_version=data.get("max_backend_version"),
            supported_platforms=data.get("supported_platforms", ["linux", "windows"]),
            source=source,
            requires_root=data.get("requires_root", False),
            requires_network=data.get("requires_network", False),
            requires_docker=data.get("requires_docker", False),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "version": self.version,
            "author": self.author,
            "description": self.description,
            "long_description": self.long_description,
            "category": self.category.value,
            "tags": self.tags,
            "homepage": self.homepage,
            "repository": self.repository,
            "documentation": self.documentation,
            "icon": self.icon,
            "dependencies": self.dependencies,
            "python_deps": self.python_deps,
            "system_deps": self.system_deps,
            "min_backend_version": self.min_backend_version,
            "max_backend_version": self.max_backend_version,
            "supported_platforms": self.supported_platforms,
            "source": self.source.value,
            "requires_root": self.requires_root,
            "requires_network": self.requires_network,
            "requires_docker": self.requires_docker,
        }
