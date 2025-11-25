from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
import json
from pathlib import Path
from typing import Any

from backend.ContaraNAS.core.event_bus import event_bus
from backend.ContaraNAS.core.exceptions import ModuleError, ModuleInitializationError
from backend.ContaraNAS.core.utils import get_logger


logger = get_logger(__name__)


class ModuleCategory(Enum):
    """Categories for organizing modules"""

    MONITORING = "monitoring"
    MEDIA = "media"
    STORAGE = "storage"
    NETWORKING = "networking"
    BACKUP = "backup"
    GAMING = "gaming"
    DOWNLOADERS = "downloaders"
    HOME_AUTOMATION = "home_automation"
    DEVELOPMENT = "development"
    OTHER = "other"


class ModuleSource(Enum):
    """Source/origin of a module"""

    BUILTIN = "builtin"
    COMMUNITY = "community"
    LOCAL = "local"


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


class Module(ABC):
    """Base class for all modules"""

    def __init__(self, name: str, display_name: str | None = None):
        self.name: str = name
        self.display_name: str = display_name or name.replace("_", " ").title()
        self.enable_flag: bool = False
        self.init_flag: bool = False
        self.state: dict[str, Any] = {}

        # Load metadata from module.json
        self._metadata: ModuleMetadata | None = None

    @property
    def metadata(self) -> ModuleMetadata:
        """Get module metadata, loading from module.json if needed"""
        if self._metadata is None:
            self._metadata = self._load_metadata()
        return self._metadata

    def _load_metadata(self) -> ModuleMetadata:
        """Load metadata from module.json in the module's directory"""
        # Find the module's directory (where __init__.py is)
        Path(self.__class__.__module__.replace(".", "/") + ".py")

        # Try to find module.json in common locations
        possible_paths = [
            # Alongside __init__.py in package
            Path(self.__class__.__module__.replace(".", "/")).parent / "module.json",
            # In the module package directory
            Path(__file__).parent.parent / "modules" / self.name / "module.json",
        ]

        for json_path in possible_paths:
            if json_path.exists():
                try:
                    with open(json_path, encoding="utf-8") as f:
                        data = json.load(f)
                    logger.debug(f"Loaded metadata for {self.name} from {json_path}")
                    return ModuleMetadata.from_dict(data)
                except (json.JSONDecodeError, OSError) as e:
                    logger.warning(f"Failed to load module.json for {self.name}: {e}")

        logger.debug(f"No module.json found for {self.name}, using defaults")
        return ModuleMetadata()

    @abstractmethod
    async def initialize(self):
        """One-time setup when module is enabled"""

    @abstractmethod
    async def start_monitoring(self):
        """Start event handlers/watchers"""

    @abstractmethod
    async def stop_monitoring(self):
        """Stop all event handlers/watchers"""

    @abstractmethod
    async def get_tile_data(self):
        """Get data for dashboard tile display"""

    async def enable(self):
        """Enable the module and start monitoring"""
        if self.enable_flag:
            logger.debug(f"Module {self.name} is already enabled")
            return

        try:
            if not self.init_flag:
                await self.initialize()
                self.init_flag = True

            if not self.init_flag:
                raise RuntimeError(f"Cannot enable module {self.name}: not initialized")

            await self.start_monitoring()
            self.enable_flag = True
            logger.info(f"Module {self.name} enabled successfully")
        except Exception as e:
            raise ModuleInitializationError(self.name, str(e)) from e

        await self._emit_event("enabled")

    async def disable(self):
        """Disable the module and stop monitoring"""
        if not self.enable_flag:
            logger.debug(f"Module {self.name} is already disabled")
            return

        try:
            await self.stop_monitoring()
            self.enable_flag = False
            logger.info(f"Module {self.name} disabled successfully")
            await self._emit_event("disabled")
        except Exception as e:
            logger.error(f"Failed to disable module {self.name}: {e!s}")
            raise ModuleError(self.name, str(e)) from e

    async def update_state(self, **kwargs):
        """Update module state"""
        old_state = self.state.copy()
        self.state.update(kwargs)
        logger.debug(f"Module {self.name} state updated: {kwargs}")

        await self._emit_event(
            "state_updated",
            {
                "module_name": self.name,
                "old_state": old_state,
                "new_state": self.state,
                "changes": kwargs,
            },
        )

    async def _emit_event(self, change_type: str, data: dict | None = None):
        """Emit state change event"""
        event_data = {
            "name": self.name,
            "display_name": self.display_name,
            "enabled": self.enable_flag,
            "initialized": self.init_flag,
            "state": self.state.copy(),
            "tile_data": await self.get_tile_data(),
            "change_type": change_type,
            "metadata": self.metadata.to_dict(),
        }

        if data:
            event_data.update(data)

        event_bus.emit(f"module.{self.name}.state_changed", event_data)
