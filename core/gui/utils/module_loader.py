import importlib.util
import os
from core.utils import get_logger
from core.module import Module

logger = get_logger(__name__)


class ModuleLoader:
    def __init__(self, module_dirs=None):
        if module_dirs is None:
            module_dirs = ["modules", "community_modules"]

        self.module_dirs = module_dirs
        self.modules = {}

    def discover_modules(self):
        for module_dir in self.module_dirs:
            if not os.path.exists(module_dir):
                continue

            for entry in os.scandir(module_dir):
                logger.debug(entry)

                if entry.is_dir() and os.path.exists(os.path.join(entry.path, "__init__.py")):
                    module_name = entry.name
                    logger.info(f"Discovered module {module_name}")
                    module_path = os.path.join(entry.path, "__init__.py")
                    self.load_module(module_name, module_path)

    def load_module(self, module_name, module_path):
        unique_module_name = f"modules.{module_name}"
        logger.debug(f"Attempting to load module '{unique_module_name}' from path: {module_path}")

        try:
            spec = importlib.util.spec_from_file_location(unique_module_name, module_path)
            logger.debug(f"Spec: {spec}")

            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                logger.debug(f"Module object created: {module}")
                spec.loader.exec_module(module)

                # Find a class that inherits from Module
                for attribute_name in dir(module):
                    attribute = getattr(module, attribute_name)

                    if isinstance(attribute, type) and issubclass(attribute, Module) and attribute != Module:
                        self.modules[module_name] = attribute
                        logger.info(f"Loaded module: '{module_name}' as '{attribute_name}'")
                        return

                logger.error(f"No valid module class found in '{module_name}'")
            else:
                logger.error(f"Failed to create spec for module: '{module_name}'")
        except Exception as e:
            logger.error(f"Error loading module '{module_name}': {e}")