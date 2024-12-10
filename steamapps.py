import os
import vdf
import json

def get_steam_libraries(steam_path):
    """
    Retrieve all Steam library paths from the libraryfolders.vdf file.

    Args:
         steam_path (str): Path to the main Steam installation directory.

    Returns:
        list: A list of paths to all Steam libraries.
    """
    library_folders_file = os.path.join(steam_path, 'steamapps', 'libraryfolders.vdf')

    with open(library_folders_file, 'r', encoding='utf-8') as f:
        libraries = vdf.load(f)['libraryfolders']

    return [libraries[key]['path'] for key in libraries if 'path' in libraries[key]]

def format_size(size_in_bytes):
    """
    Format a size in bytes into a human-readable string (GB, MB, KB).

    Args:
        size_in_bytes (int): Size in bytes.

    Returns:
        str: Formatted size string.
    """
    if size_in_bytes >= 1024 ** 3:
        return f"{size_in_bytes / (1024 ** 3):.2f} GB"
    elif size_in_bytes >= 1024 ** 2:
        return f"{size_in_bytes / (1024 ** 2):.2f} MB"
    elif size_in_bytes >= 1024:
        return f"{size_in_bytes / 1024:.2f} KB"
    else:
        return f"{size_in_bytes} B"

def get_size(path):
    """
    Recursively calculate the total size of files in a directory.

    Args:
        path (str): Directory path.

    Returns:
        int: Total size in bytes.
    """
    total_size = 0
    for root, _, files in os.walk(path):
        total_size += sum(os.path.getsize(os.path.join(root, f)) for f in files)

    return total_size

def get_installed_games(library_paths):
    """
    Retrieve information about installed games, including base game size, DLC size,
    shader cache size, and Workshop content size.

    Args:
        library_paths (list): List of Steam library paths.

    Returns:
        dict: Dictionary containing game details.
    """
    games_json = {}

    for library in library_paths:
        steamapps_path = os.path.join(library, 'steamapps')

        for file in os.listdir(steamapps_path):
            if file.startswith('appmanifest_') and file.endswith('.acf'):
                with open(os.path.join(steamapps_path, file), 'r', encoding='utf-8') as f:
                    data = vdf.load(f)
                    app_state = data.get('AppState', {})
                    name = app_state.get('name')
                    app_id = app_state.get('appid')
                    size_on_disk = int(app_state.get('SizeOnDisk', 0))

                    # Installed Depots
                    installed_depots = app_state.get('InstalledDepots', {})
                    depots_info = {}
                    dlc_size = 0

                    for depot_id, depot_data in installed_depots.items():
                        depot_size = int(depot_data.get('size', 0))

                        dlc_appid = depot_data.get('dlcappid')
                        if dlc_appid:
                            depots_info[f"DLC {dlc_appid} (Depot {depot_id})"] = format_size(depot_size)
                            dlc_size += depot_size
                        else:
                            depots_info[f"Depot {depot_id}"] = format_size(depot_size)

                    # Shader Cache Size
                    shader_cache_path = os.path.join(library, 'steamapps', 'shadercache', app_id)
                    shader_cache_size = get_size(shader_cache_path) if os.path.exists(shader_cache_path) else 0

                    # Workshop Content Size
                    workshop_content_path = os.path.join(library, 'steamapps', 'workshop', 'content', app_id)
                    workshop_content_size = get_size(workshop_content_path) if os.path.exists(workshop_content_path) else 0

                    # Add game information to the dictionary
                    games_json[name] = {
                        'app_id': app_id,
                        'location': library,
                        'size_on_disk': format_size(size_on_disk),
                        'dlc_size': format_size(dlc_size),
                        'shader_cache_size': format_size(shader_cache_size),
                        'workshop_content_size': format_size(workshop_content_size),
                        'depots': depots_info
                    }

    return games_json

if __name__ == '__main__':
    steam_path = r'C:\Program Files (x86)\Steam'
    library_paths = get_steam_libraries(steam_path)
    games = get_installed_games(library_paths)

    print(json.dumps(games, indent=2))