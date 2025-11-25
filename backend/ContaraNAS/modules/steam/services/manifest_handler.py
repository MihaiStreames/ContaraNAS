from collections.abc import Callable
from pathlib import Path
import traceback

from backend.ContaraNAS.core.utils import get_logger
from backend.ContaraNAS.modules.steam.utils import is_manifest_file
from watchdog.events import FileSystemEvent, FileSystemEventHandler


logger = get_logger(__name__)


def _ensure_str(path: str | bytes) -> str:
    """Convert path to string, handling bytes if necessary"""
    if isinstance(path, bytes):
        return path.decode("utf-8")
    return path


class SteamManifestHandler(FileSystemEventHandler):
    """Watchdog handler for Steam manifest file changes"""

    def __init__(self, callback: Callable[[str, Path], None]):
        super().__init__()
        self._callback: Callable[[str, Path], None] = callback

    def on_created(self, event: FileSystemEvent) -> None:
        if not event.is_directory:
            self._handle_manifest_event("created", _ensure_str(event.src_path))

    def on_deleted(self, event: FileSystemEvent) -> None:
        if not event.is_directory:
            self._handle_manifest_event("deleted", _ensure_str(event.src_path))

    def on_modified(self, event: FileSystemEvent) -> None:
        if not event.is_directory:
            self._handle_manifest_event("modified", _ensure_str(event.src_path))

    def on_moved(self, event: FileSystemEvent) -> None:
        # Seems like Steam uses temp files for updates
        if not event.is_directory:
            src_path_str = _ensure_str(event.src_path)
            dest_path_str = _ensure_str(event.dest_path)
            dest_path = Path(dest_path_str)

            # If moving TO a manifest file (from temp file), treat as create/update
            if is_manifest_file(dest_path_str):
                # Determine if this is a new file or an update
                if dest_path.exists():
                    self._handle_manifest_event("modified", dest_path_str)
                else:
                    self._handle_manifest_event("created", dest_path_str)

            # If moving FROM a manifest file (to backup/temp), treat as delete
            elif is_manifest_file(src_path_str):
                self._handle_manifest_event("deleted", src_path_str)

    def _handle_manifest_event(self, event_type: str, event_path: str):
        """Common handler for manifest events"""
        if not is_manifest_file(event_path):
            return

        path = Path(event_path)
        logger.info(f"Processing manifest {event_type}: {path.name}")

        try:
            self._callback(event_type, path)
        except Exception as e:
            logger.error(f"Error in callback for {event_type} {path.name}: {e}")
            logger.error(traceback.format_exc())
