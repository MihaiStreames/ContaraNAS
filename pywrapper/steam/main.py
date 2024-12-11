import json
import platform
import os

from manager import SteamGameManager


def main():
    steam_path = (
        r'C:\Program Files (x86)\Steam' if platform.system() == 'Windows'
        else os.path.expanduser('~/.steam/steam')
    )

    manager = SteamGameManager(steam_path, cache_dir=".cache/games")
    manager.load_installed_games()

    # Print a summary of loaded games and their basic info
    for game in manager.games:
        print(f"Game: {game.name} (AppID: {game.app_id})")
        print(f"  Location: {game.library_path}")
        print(f"  Store Page: {game.store_page_url}")
        print(f"  Cover Image URL: {game.cover_image_url}")
        print(f"  Size on Disk: {game.size_on_disk}")
        print(f"  DLC Size: {game.dlc_size}")
        print(f"  Shader Cache Size: {game.shader_cache_size}")
        print(f"  Workshop Content Size: {game.workshop_content_size}")
        print("  Depots:")
        for depot_key, depot_val in game.depots.items():
            print(f"    {depot_key}: {depot_val}")
        print("-" * 80)

    serialized_data = manager.serialize_games()
    with open("games_data.json", "w", encoding="utf-8") as f:
        json.dump(serialized_data, f, indent=4)

    print("Games data has been serialized to games_data.json")

if __name__ == "__main__":
    main()