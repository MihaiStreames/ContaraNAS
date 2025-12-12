import importlib
import json
from pathlib import Path

from ContaraNAS.core.module import Module, ModuleMetadata
from ContaraNAS.core import get_logger


logger = get_logger(__name__)


class ModuleLoader:
    """Discovers and loads modules from filesystem"""

    def __init__(self):
        self.modules_base = Path(__file__).parent
        self.builtin_dir = self.modules_base / "builtin"
        self.community_dir = self.modules_base / "community"

        # module_id -> (metadata, path)
        self._discovered: dict[str, tuple[ModuleMetadata, Path]] = {}

    def _scan_directory(self, directory: Path, source: str) -> None:
        """Scan a directory for valid modules"""
        if not directory.exists():
            logger.debug(f"Module directory does not exist: {directory}")
            return

        for module_dir in directory.iterdir():
            if not module_dir.is_dir():
                continue

            metadata = self._load_metadata(module_dir, source)

            if metadata:
                self._discovered[metadata.id] = (metadata, module_dir)

    @staticmethod
    def _load_metadata(module_dir: Path, source: str) -> ModuleMetadata | None:
        """Load and validate metadata from a module directory"""
        metadata_file = module_dir / "module.json"
        init_file = module_dir / "__init__.py"

        if not metadata_file.exists() or not init_file.exists():
            return None

        try:
            with metadata_file.open(encoding="utf-8") as f:
                data = json.load(f)

            return ModuleMetadata.from_json(data, source=source)

        except Exception as e:
            logger.error(f"Failed to load metadata for {module_dir.name}: {e}")
            return None

    @staticmethod
    def _find_module_class(module) -> type[Module] | None:
        """Find the Module subclass in a loaded module"""
        for attr_name in dir(module):
            attr = getattr(module, attr_name)

            # Check if it's a class that inherits from Module
            if isinstance(attr, type) and issubclass(attr, Module) and attr is not Module:
                return attr

        return None

    def discover(self) -> dict[str, tuple[ModuleMetadata, Path]]:
        """Discover all available modules"""
        self._discovered.clear()

        self._scan_directory(self.builtin_dir, source="builtin")
        self._scan_directory(self.community_dir, source="community")

        logger.info(f"Discovered {len(self._discovered)} modules")
        return self._discovered.copy()

    def load_module_class(self, module_id: str) -> type[Module]:
        """Dynamically load a module's class"""
        if module_id not in self._discovered:
            raise ValueError(f"Module '{module_id}' not found")

        _, module_path = self._discovered[module_id]
        relative_path = module_path.relative_to(self.modules_base)
        import_path = f"ContaraNAS.modules.{'.'.join(relative_path.parts)}"

        try:
            module = importlib.import_module(import_path)

            # Find Module subclass
            for attr_name in dir(module):
                attr = getattr(module, attr_name)

                if isinstance(attr, type) and issubclass(attr, Module) and attr is not Module:
                    return attr

            raise ImportError(f"No Module subclass in {import_path}")

        except Exception as e:
            logger.error(f"Failed to load module {module_id}: {e}")
            raise ImportError(f"Failed to load module {module_id}") from e

    def get_metadata(self, module_id: str) -> ModuleMetadata | None:
        """Get metadata for a specific module"""
        if module_id in self._discovered:
            return self._discovered[module_id][0]

        return None


module_loader = ModuleLoader()
