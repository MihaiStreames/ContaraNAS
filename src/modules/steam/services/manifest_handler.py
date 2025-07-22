from pathlib import Path
from typing import Callable

from watchdog.events import FileSystemEventHandler, FileSystemEvent

from src.core.utils import get_logger

logger = get_logger(__name__)


class SteamManifestHandler(FileSystemEventHandler):
    """Watchdog handler for Steam manifest files"""

    def __init__(self, callback: Callable[[str, Path], None]):
        super().__init__()
        self.callback = callback

    def on_created(self, event: FileSystemEvent):
        if not event.is_directory and event.src_path.endswith('.acf'):
            path = Path(event.src_path)
            if path.name.startswith('appmanifest_'):
                logger.debug(f"Manifest created: {path}")
                self.callback('created', path)

    def on_deleted(self, event: FileSystemEvent):
        if not event.is_directory and event.src_path.endswith('.acf'):
            path = Path(event.src_path)
            if path.name.startswith('appmanifest_'):
                logger.debug(f"Manifest deleted: {path}")
                self.callback('deleted', path)

    def on_modified(self, event: FileSystemEvent):
        if not event.is_directory and event.src_path.endswith('.acf'):
            path = Path(event.src_path)
            if path.name.startswith('appmanifest_'):
                logger.debug(f"Manifest modified: {path}")
                self.callback('modified', path)
