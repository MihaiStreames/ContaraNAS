import os
import vdf

from manager import SteamGame


class SteamGameManager:
    def __init__(self, steam_path, cache_dir=".cache/games"):
        self.steam_path = steam_path
        self.cache_dir = cache_dir
        self.games = []

    def load_installed_games(self):
        library_paths = self.get_steam_libraries()
        for library in library_paths:
            steamapps_path = os.path.join(library, 'steamapps')

            for file in os.listdir(steamapps_path):
                if file.startswith('appmanifest_') and file.endswith('.acf'):
                    app_id = file.split('_')[1].split('.')[0]
                    manifest_path = os.path.join(steamapps_path, file)

                    with open(manifest_path, 'r', encoding='utf-8') as f:
                        data = vdf.load(f).get('AppState', {})
                        name = data.get('name')

                        if app_id and name:
                            game = SteamGame(app_id, name, library, self.cache_dir)

                            if game.has_new_depots():
                                game.update_depots()
                                game.save_to_cache()

                            self.games.append(game)

    def get_steam_libraries(self):
        library_folders_file = os.path.join(self.steam_path, 'steamapps', 'libraryfolders.vdf')
        try:
            with open(library_folders_file, 'r', encoding='utf-8') as f:
                libraries = vdf.load(f).get('libraryfolders', {})
                return [lib['path'] for lib in libraries.values() if 'path' in lib]

        except (FileNotFoundError, KeyError):
            print(f"Error: Unable to load library folders from {library_folders_file}")
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
                "depots": game.depots
            })

        return serialized