import os
import platform
import vdf
import json

from steam_helpers import format_size, get_size, check_url, parse_span
from depot_info import get_depot_details

def get_steam_libraries(steam_path):
    """
    Retrieves all Steam library paths from the libraryfolders.vdf file.

    Args:
         steam_path (str): Path to the main Steam installation directory.

    Returns:
        list: List of paths to all Steam libraries.
    """
    library_folders_file = os.path.join(steam_path, 'steamapps', 'libraryfolders.vdf')

    try:
        with open(library_folders_file, 'r', encoding='utf-8') as f:
            libraries = vdf.load(f)['libraryfolders']
            return [lib['path'] for lib in libraries.values() if 'path' in lib]

    except (FileNotFoundError, KeyError):
        print(f"Error: Unable to load library folders from {library_folders_file}")
        return []

def get_installed_games(library_paths):
    """
    Retrieves information about locally installed Steam games.

    Args:
        library_paths (list[str]): List of paths to Steam library directories.

    Returns:
        dict: Dictionary where each key is the game's name, and the value is another dictionary containing the following details:

            - app_id (str): AppID of the game.
            - location (str): Path to the Steam library where the game is installed.
            - cover_image_url (str): URL to the game's cover image.
            - store_page_url (str or None): URL to the game's Steam store page. Returns None if there is no store page for the game.
            - size_on_disk (str): Size of the base game installation.
            - dlc_size (str): Total size of installed DLCs.
            - shader_cache_size (str): Total size of the shader cache.
            - workshop_content_size (str): Total size of workshop content.
            - depots (dict): Dictionary containing depot details.
    """
    games_json = {}

    for library in library_paths:
        steamapps_path = os.path.join(library, 'steamapps')

        for file in os.listdir(steamapps_path):
            if not (file.startswith('appmanifest_') and file.endswith('.acf')):
                continue

            with open(os.path.join(steamapps_path, file), 'r', encoding='utf-8') as f:
                data = vdf.load(f)
                app_state = data.get('AppState', {})
                name = app_state.get('name')
                app_id = app_state.get('appid')
                size_on_disk = int(app_state.get('SizeOnDisk', 0))

                ### Installed Depots and DLCs
                installed_depots = app_state.get('InstalledDepots', {})
                depots_info = {}
                dlc_size = 0

                # Depot details from SteamDB (! do not overuse !)
                try:
                    depot_details = get_depot_details(app_id)
                    if depot_details is None:
                        raise Exception("No depot details returned.")

                    rate_limited = False

                except Exception as e:
                    print(f"SteamDB rate-limited or error occurred for AppID {app_id}: {e}")
                    depot_details = []
                    rate_limited = True

                for depot_id, depot_data in installed_depots.items():
                    depot_size = int(depot_data.get('size', 0))
                    dlc_appid = depot_data.get('dlcappid')

                    if rate_limited:
                        # Fallback case if rate-limited
                        if dlc_appid:
                            depots_info[f"(DLC ID {dlc_appid}) (DEPOT ID {depot_id})"] = format_size(depot_size)
                            dlc_size += depot_size
                        else:
                            depots_info[f"(DEPOT ID {depot_id})"] = format_size(depot_size)
                    else:
                        # Normal case
                        depot_name = next(
                            (parse_span(d['details']) for d in depot_details if d['depot_id'] == depot_id),
                            f"Depot {depot_id}"
                        )

                        formatted_depot_name = f"({depot_id}) {depot_name}"

                        if dlc_appid:
                            dlc_name = next(
                                (parse_span(d['details']) for d in depot_details if d['depot_id'] == dlc_appid),
                                f"DLC {dlc_appid}"
                            )

                            depots_info[f"({dlc_appid}) {dlc_name}"] = format_size(depot_size)
                            dlc_size += depot_size
                        else:
                            depots_info[formatted_depot_name] = format_size(depot_size)

                ### Additional Sizes
                # Shader Cache Size
                shader_cache_path = os.path.join(library, 'steamapps', 'shadercache', app_id)
                shader_cache_size = format_size(get_size(shader_cache_path) if os.path.exists(shader_cache_path) else 0)

                # Workshop Content Size
                workshop_content_path = os.path.join(library, 'steamapps', 'workshop', 'content', app_id)
                workshop_content_size = format_size(get_size(workshop_content_path) if os.path.exists(workshop_content_path) else 0)

                ### URLs
                # Cover Image URL
                cover_image_url = f"https://steamcdn-a.akamaihd.net/steam/apps/{app_id}/header.jpg"

                # Store Page URL
                if check_url(url := f"https://store.steampowered.com/app/{app_id}/"):
                    store_page_url = url
                else:
                    store_page_url = None

                ### Everything goes here
                games_json[name] = {
                    'app_id': app_id,
                    'location': library,
                    'cover_image_url': cover_image_url,
                    'store_page_url': store_page_url,
                    'size_on_disk': format_size(size_on_disk),
                    'dlc_size': format_size(dlc_size),
                    'shader_cache_size': shader_cache_size,
                    'workshop_content_size': workshop_content_size,
                    'depots': depots_info
                }

    return games_json

if __name__ == '__main__':
    steam_pth = (
        r'C:\Program Files (x86)\Steam' if platform.system() == 'Windows'
        else os.path.expanduser('~/.steam/steam')
    )

    lib_pths = get_steam_libraries(steam_pth)
    games = get_installed_games(lib_pths)

    print(json.dumps(games, indent=2))