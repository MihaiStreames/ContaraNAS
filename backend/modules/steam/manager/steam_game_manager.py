import os

import requests
import vdf

from backend.core.utils import get_logger
from .steam_game import SteamGame

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
            logger.debug(f"Checking for updates for {name} (AppID: {app_id})")

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

            if not os.path.exists(steamapps_path):
                logger.warning(f"Steam library path does not exist: {steamapps_path}")
                continue

            for file in os.listdir(steamapps_path):
                if file.startswith('appmanifest_') and file.endswith('.acf'):
                    try:
                        game = self._process_manifest(library, file)
                        if game:
                            self.games.append(game)
                    except Exception as e:
                        logger.error(f"Error processing manifest {file}: {e}")

    @staticmethod
    def cache_cover(game):
        images_dir = os.path.join('resources', 'images', 'steam')
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
                logger.debug(f"Successfully cached cover image for {game.name}")
            else:
                logger.warning(f"Cover image not available for {game.name} (HTTP {response.status_code})")
        except requests.RequestException as e:
            logger.warning(f"Failed to cache cover image for {game.name} (AppID: {game.app_id}): {e}")

    def get_steam_libs(self):
        library_folders_file = os.path.join(self.steam_path, 'steamapps', 'libraryfolders.vdf')

        try:
            with open(library_folders_file, 'r', encoding='utf-8') as f:
                libraries = vdf.load(f).get('libraryfolders', {})
                paths = [lib['path'] for lib in libraries.values() if 'path' in lib]
                logger.info(f"Found {len(paths)} Steam library paths: {paths}")
                return paths
        except (FileNotFoundError, KeyError) as e:
            logger.error(f"Error: Unable to load library folders from {library_folders_file}: {e}")
            return []

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
                "total_size": game.get_total_size(),
                "depots": game.depots,
                # Formatted versions for display
                "formatted_size_on_disk": game.get_formatted_size_on_disk(),
                "formatted_dlc_size": game.get_formatted_dlc_size(),
                "formatted_shader_cache_size": game.get_formatted_shader_cache_size(),
                "formatted_workshop_content_size": game.get_formatted_workshop_content_size(),
                "formatted_total_size": game.get_formatted_size_on_disk()
            })

        logger.info(f"Serialized {len(serialized)} games")
        return serialized
