import platform
import os

from core.utils import get_logger
from core.module import Module

logger = get_logger(__name__)


class SteamModule(Module):
    def __init__(self, main_window):
        super().__init__(main_window)
        self.steam_path = self.get_steam_path()
        self.cache_dir = ".cache/games"
        self.loader = None
        self.loading_screen = None
        self.initialized = False

    def get_steam_path(self):
        if platform.system() == 'Windows':
            return r'C:\Program Files (x86)\Steam'
        else:
            return os.path.expanduser('~/.steam/steam')

    def initialize(self):
        logger.info("Initializing Steam module")

        from .gui.steam_page import SteamPage
        from .gui.loading_screen import LoadingScreen
        from .utils.cache_loader import CacheLoader

        def launch_steam_page(loader):
            logger.info("Caching complete")
            serialized_games = loader.manager.serialize_games()
            data = {game["name"]: game for game in serialized_games}

            steam_page = SteamPage(data, self.main_window)
            self.main_window.set_module_page(steam_page)
            logger.info("Steam page loaded")

        self.loader = CacheLoader(self.steam_path, self.cache_dir)
        self.loading_screen = LoadingScreen(self.loader, lambda: launch_steam_page(self.loader))
        self.initialized = True

    def execute(self):
        logger.info("Executing Steam module")
        if not self.initialized:
            self.initialize()

        if self.loader and self.loading_screen:
            self.loading_screen.show()
            self.loader.start()
        else:
            logger.error("Loader or loading screen not initialized.")