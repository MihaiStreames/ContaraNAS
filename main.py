import os
import platform
import sys

from PySide6.QtWidgets import QApplication
from core.utils import CacheLoader, get_logger
from modules.steam.gui import LoadingScreen, MainWindow

logger = get_logger(__name__)


def main():
    global main_window  # Ensure main_window stays in scope

    if platform.system() == 'Windows':
        steam_path = r'C:\Program Files (x86)\Steam'
    else:
        steam_path = os.path.expanduser('~/.steam/steam')

    app = QApplication(sys.argv)

    loader = CacheLoader(steam_path, cache_dir=".cache/games")
    loading_screen = LoadingScreen(loader, lambda: launch_main_window(loader))
    loading_screen.show()

    def launch_main_window(loader):
        logger.info("Caching complete. Attempting to launch main window...")
        serialized_games = loader.manager.serialize_games()
        data = {game["name"]: game for game in serialized_games}

        global main_window
        main_window = MainWindow(data)
        main_window.show()
        main_window.raise_()
        main_window.activateWindow()
        logger.info("Main window launched successfully.")

    loader.start()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()