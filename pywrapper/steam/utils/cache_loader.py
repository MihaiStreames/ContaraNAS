from PySide6.QtCore import QThread, Signal
from manager import SteamGameManager
from utils import get_logger

logger = get_logger(__name__)


class CacheLoader(QThread):
    finished = Signal()
    progress = Signal(int)

    def __init__(self, steam_path, cache_dir=".cache/games"):
        super().__init__()
        self.manager = SteamGameManager(steam_path, cache_dir)

    def run(self):
        try:
            logger.info("CacheLoader started.")
            self.manager.load_games_progress(self.emit_progress)
            logger.info("CacheLoader finished successfully.")
        except Exception as e:
            logger.error(f"Error in CacheLoader: {e}")
        finally:
            logger.info("CacheLoader thread quitting.")
            self.finished.emit()
            self.quit()

    def emit_progress(self, value):
        self.progress.emit(value)