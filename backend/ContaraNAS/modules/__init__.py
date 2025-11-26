import importlib
import json
from pathlib import Path

from backend.ContaraNAS.core.module import Module, ModuleMetadata
from backend.ContaraNAS.core.utils import get_logger

logger = get_logger(__name__)


class ModuleLoader:
    """Discovers and loads modules from filesystem"""

    def __init__(self):
        self.modules_base = Path(__file__).parent
        self.builtin_dir = self.modules_base / "builtin"
        self.community_dir = self.modules_base / "community"

        self._discovered_modules: dict[str, tuple[ModuleMetadata, Path]] = {}

    def discover(self) -> dict[str, tuple[ModuleMetadata, Path]]:
        """Discover all available modules"""
        self._discovered_modules.clear()

        self._discover_in_directory(self.builtin_dir, source="builtin")
        self._discover_in_directory(self.community_dir, source="community")

        logger.info(f"Discovered {len(self._discovered_modules)} modules")
        return self._discovered_modules.copy()

    def _discover_in_directory(self, directory: Path, source: str) -> None:
        """Discover modules in a specific directory"""
        if not directory.exists():
            logger.warning(f"Module directory does not exist: {directory}")
            return

        for module_dir in directory.iterdir():
            if not module_dir.is_dir():
                continue

            # Check for module.json
            metadata_file = module_dir / "module.json"
            if not metadata_file.exists():
                logger.debug(f"Skipping {module_dir.name}: no module.json")
                continue

            # Check for __init__.py
            init_file = module_dir / "__init__.py"
            if not init_file.exists():
                logger.warning(f"Skipping {module_dir.name}: no __init__.py")
                continue

            try:
                # Load metadata
                with metadata_file.open(encoding="utf-8") as f:
                    metadata_data = json.load(f)

                metadata = ModuleMetadata.from_json(metadata_data, source=source)

                # Store discovery
                self._discovered_modules[metadata.id] = (metadata, module_dir)
                logger.debug(f"Discovered {source} module: {metadata.id}")

            except Exception as e:
                logger.error(f"Failed to load metadata for {module_dir.name}: {e}")

    def load_module(self, module_id: str) -> type[Module]:
        """Dynamically load a module class"""
        if module_id not in self._discovered_modules:
            raise ValueError(f"Module '{module_id}' not found")

        metadata, module_path = self._discovered_modules[module_id]

        # Construct module import path
        relative_path = module_path.relative_to(self.modules_base)
        import_path = f"ContaraNAS.modules.{'.'.join(relative_path.parts)}"

        try:
            logger.info(f"Loading module: {import_path}")
            module = importlib.import_module(import_path)

            # Find the Module subclass
            module_class = self._find_module_class(module)

            if not module_class:
                raise ImportError(f"No Module subclass found in {import_path}")

            return module_class

        except Exception as e:
            logger.error(f"Failed to load module {module_id}: {e}")
            raise ImportError(f"Failed to load module {module_id}") from e

    def get_metadata(self, module_id: str) -> ModuleMetadata | None:
        """Get metadata for a specific module"""
        if module_id in self._discovered_modules:
            return self._discovered_modules[module_id][0]
        return None

    @staticmethod
    def _find_module_class(module) -> type[Module] | None:
        """Find the Module subclass in a loaded module"""
        for attr_name in dir(module):
            attr = getattr(module, attr_name)

            # Check if it's a class that inherits from Module
            if (
                    isinstance(attr, type)
                    and issubclass(attr, Module)
                    and attr is not Module
            ):
                return attr

        return None

    def get_all_metadata(self) -> list[ModuleMetadata]:
        """Get metadata for all discovered modules"""
        return [metadata for metadata, _ in self._discovered_modules.values()]


# Global module loader instance
module_loader = ModuleLoader()