from pathlib import Path
import traceback

from watchdog.events import FileSystemEvent, FileSystemEventHandler

from ContaraNAS.core.utils import get_logger
from ContaraNAS.modules.steam.utils import is_manifest_file


logger = get_logger(__name__)


class SteamManifestHandler(FileSystemEventHandler):
    """Watchdog handler for Steam manifest file changes"""

    def __init__(self, callback):
        super().__init__()
        self.callback = callback

    def on_created(self, event: FileSystemEvent):
        if not event.is_directory:
            self._handle_manifest_event("created", event.src_path)

    def on_deleted(self, event: FileSystemEvent):
        if not event.is_directory:
            self._handle_manifest_event("deleted", event.src_path)

    def on_modified(self, event: FileSystemEvent):
        if not event.is_directory:
            self._handle_manifest_event("modified", event.src_path)

    def on_moved(self, event: FileSystemEvent):
        # Seems like Steam uses temp files for updates
        if not event.is_directory:
            Path(event.src_path)
            dest_path = Path(event.dest_path)

            # If moving TO a manifest file (from temp file), treat as create/update
            if is_manifest_file(event.dest_path):
                # Determine if this is a new file or an update
                if dest_path.exists():
                    self._handle_manifest_event("modified", event.dest_path)
                else:
                    self._handle_manifest_event("created", event.dest_path)

            # If moving FROM a manifest file (to backup/temp), treat as delete
            elif is_manifest_file(event.src_path):
                self._handle_manifest_event("deleted", event.src_path)

    def _handle_manifest_event(self, event_type: str, event_path: str):
        """Common handler for manifest events"""
        if not is_manifest_file(event_path):
            return

        path = Path(event_path)
        logger.info(f"Processing manifest {event_type}: {path.name}")

        try:
            self.callback(event_type, path)
        except Exception as e:
            logger.error(f"Error in callback for {event_type} {path.name}: {e}")
            logger.error(traceback.format_exc())
