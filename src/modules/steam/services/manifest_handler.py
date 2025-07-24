from pathlib import Path

from watchdog.events import FileSystemEventHandler, FileSystemEvent

from src.core.utils import get_logger

logger = get_logger(__name__)


class SteamManifestHandler(FileSystemEventHandler):
    """Watchdog handler for Steam manifest file changes"""

    def __init__(self, callback):
        super().__init__()
        self.callback = callback

    def _handle_manifest_event(self, event_type: str, event_path: str):
        """Common handler for manifest events"""
        if not event_path.endswith('.acf'):
            return

        path = Path(event_path)
        if not path.name.startswith('appmanifest_'):
            return

        logger.debug(f"Watchdog event: {event_type} -> {path.name}")

        self.callback(event_type, path)

    def on_created(self, event: FileSystemEvent):
        if not event.is_directory:
            self._handle_manifest_event('created', event.src_path)

    def on_deleted(self, event: FileSystemEvent):
        if not event.is_directory:
            self._handle_manifest_event('deleted', event.src_path)

    def on_modified(self, event: FileSystemEvent):
        if not event.is_directory:
            self._handle_manifest_event('modified', event.src_path)

    def on_moved(self, event: FileSystemEvent):
        if not event.is_directory:
            # Handle moves as delete + create
            self._handle_manifest_event('deleted', event.src_path)
            self._handle_manifest_event('created', event.dest_path)
