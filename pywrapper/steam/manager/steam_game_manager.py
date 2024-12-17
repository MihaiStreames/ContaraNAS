import os
import vdf
import requests
import threading

from concurrent.futures import ThreadPoolExecutor
from manager import SteamGame
from utils import get_logger

logger = get_logger(__name__)


class SteamGameManager:
    def __init__(self, steam_path, cache_dir=".cache/games"):
        self.steam_path = steam_path
        self.cache_dir = cache_dir
        self.games = []

        logger.info("SteamGameManager initialized.")

    def _process_manifest(self, library, file):
        app_id = file.split('_')[1].split('.')[0]
        manifest_path = os.path.join(library, 'steamapps', file)

        logger.debug(f"Processing manifest: {manifest_path}")

        with open(manifest_path, 'r', encoding='utf-8') as f:
            data = vdf.load(f).get('AppState', {})
            name = data.get('name')

        if app_id and name:
            game = SteamGame(app_id, name, library, self.cache_dir)
            logger.debug(f"Checking for new depots for {name} (AppID: {app_id})")

            if game.has_new_depots():
                game.update_depots()

            self.cache_cover(game)
            game.save_to_cache()
            return game

        return None

    def load_games(self):
        library_paths = self.get_steam_libs()
        logger.info("Loading installed games from libraries.")

        for library in library_paths:
            steamapps_path = os.path.join(library, 'steamapps')

            for file in os.listdir(steamapps_path):
                if file.startswith('appmanifest_') and file.endswith('.acf'):
                    game = self._process_manifest(library, file)

                    if game:
                        self.games.append(game)

    def load_games_progress(self, progress_callback):
        library_paths = self.get_steam_libs()
        logger.info("Loading installed games with progress tracking.")

        with ThreadPoolExecutor() as executor:
            futures = []

            for library in library_paths:
                steamapps_path = os.path.join(library, 'steamapps')

                for file in os.listdir(steamapps_path):
                    if file.startswith('appmanifest_') and file.endswith('.acf'):
                        futures.append(executor.submit(self._process_manifest, library, file))

            for i, future in enumerate(futures):
                game = future.result()

                if game:
                    self.games.append(game)
                progress_callback(int((i + 1) / len(futures) * 100))

        logger.info("All games have been loaded successfully.")

    def cache_cover(self, game):
        images_dir = os.path.join('resources', 'images')
        os.makedirs(images_dir, exist_ok=True)
        image_path = os.path.join(images_dir, f"{game.app_id}.jpg")

        if os.path.exists(image_path):
            logger.debug(f"Cover image already exists for {game.name} (AppID: {game.app_id}), skipping download.")
            return

        logger.debug(f"Caching cover image for {game.name} (AppID: {game.app_id})")

        try:
            response = requests.head(game.cover_image_url, timeout=5)
            if response.status_code == 200:
                with open(image_path, 'wb') as f:
                    f.write(requests.get(game.cover_image_url).content)
        except requests.RequestException as e:
            logger.warning(f"Failed to cache cover image for {game.name} (AppID: {game.app_id}): {e}")

    def get_steam_libs(self):
        library_folders_file = os.path.join(self.steam_path, 'steamapps', 'libraryfolders.vdf')

        try:
            with open(library_folders_file, 'r', encoding='utf-8') as f:
                libraries = vdf.load(f).get('libraryfolders', {})
                return [lib['path'] for lib in libraries.values() if 'path' in lib]
        except (FileNotFoundError, KeyError):
            logger.error(f"Error: Unable to load library folders from {library_folders_file}")
            return []

    def check_new_games(self):
        current_game_ids = {game.app_id for game in self.games}
        library_paths = self.get_steam_libs()

        for library in library_paths:
            steamapps_path = os.path.join(library, 'steamapps')

            for file in os.listdir(steamapps_path):
                if file.startswith('appmanifest_') and file.endswith('.acf'):
                    app_id = file.split('_')[1].split('.')[0]

                    if app_id not in current_game_ids:
                        logger.info(f"New game detected: AppID {app_id}")
                        self.load_games()
                        break

    def periodic_check(self, interval=3600):
        logger.info("Starting periodic update checks.")

        self.check_new_games()

        for game in self.games:
            game.quick_size_check()

            if game.has_new_depots():
                game.update_depots()
                game.save_to_cache()

        threading.Timer(interval, self.periodic_check).start()

    def serialize_games(self):
        serialized = []

        for game in self.games:
            serialized.append({
                "app_id": game.app_id,
                "name": game.name,
                "location": game.library_path,
                "cover_image_url": game.cover_image_url,
                "store_page_url": game.store_page_url,
                "size_on_disk": game.size_on_disk,
                "dlc_size": game.dlc_size,
                "shader_cache_size": game.shader_cache_size,
                "workshop_content_size": game.workshop_content_size,
                "depots": game.depots
            })

        return serialized