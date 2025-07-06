import os
import platform

from backend.core.module import Module
from backend.core.utils import get_logger

logger = get_logger(__name__)


class SteamModule(Module):
    def __init__(self):
        super().__init__()
        self.steam_path = self.get_steam_path()
        self.cache_dir = ".cache/games"

    @staticmethod
    def get_steam_path():
        if platform.system() == 'Windows':
            return r'C:\Program Files (x86)\Steam'
        else:
            return os.path.expanduser('~/.steam/steam')

    def get_module_info(self):
        """Get basic module information"""
        return {
            "name": "steam",
            "title": "Steam Library",
            "description": "Game collection overview",
            "version": "1.0.0"
        }

    def get_tile_data(self):
        """Get quick data for the tile display"""
        try:
            from .manager.steam_game_manager import SteamGameManager

            # Quick initialization for tile data
            manager = SteamGameManager(self.steam_path, self.cache_dir)
            library_paths = manager.get_steam_libs()

            drives_data = {}

            for lib_path in library_paths:
                drive = os.path.splitdrive(lib_path)[0] if os.name == 'nt' else '/'

                if drive not in drives_data:
                    drives_data[drive] = {
                        'drive_size': self.get_drive_size(drive),
                        'total_games_size': 0,
                        'dlc_size': 0,
                        'workshop_size': 0,
                        'shader_size': 0,
                        'updates_size': 0,
                    }

                # Get quick size estimates from cache or manifests
                lib_data = self.get_library_sizes(lib_path)
                for key, value in lib_data.items():
                    drives_data[drive][key] += value

            return {'drives': drives_data}

        except Exception as e:
            logger.error(f"Error getting Steam tile data: {e}")
            return {'drives': {}}

    def get_drive_size(self, drive_path):
        """Get total drive size"""
        try:
            if os.name == 'nt':  # Windows
                import ctypes
                free_bytes = ctypes.c_ulonglong(0)
                total_bytes = ctypes.c_ulonglong(0)
                ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                    ctypes.c_wchar_p(drive_path),
                    ctypes.pointer(free_bytes),
                    ctypes.pointer(total_bytes),
                    None
                )
                return total_bytes.value
            else:  # Unix-like
                statvfs = os.statvfs(drive_path)
                return statvfs.f_frsize * statvfs.f_blocks
        except:
            return 0

    def get_library_sizes(self, library_path):
        """Get quick size estimates for a library"""
        try:
            steamapps_path = os.path.join(library_path, 'steamapps')

            sizes = {
                'total_games_size': 0,
                'dlc_size': 0,
                'workshop_size': 0,
                'shader_size': 0,
            }

            # Quick estimate from manifest files
            if os.path.exists(steamapps_path):
                import vdf

                for file in os.listdir(steamapps_path):
                    if file.startswith('appmanifest_') and file.endswith('.acf'):
                        manifest_path = os.path.join(steamapps_path, file)
                        try:
                            with open(manifest_path, 'r', encoding='utf-8') as f:
                                data = vdf.load(f).get('AppState', {})
                                game_size = int(data.get('SizeOnDisk', 0))
                                sizes['total_games_size'] += game_size
                        except:
                            continue

                # Quick estimates for other content
                workshop_path = os.path.join(steamapps_path, 'workshop')
                if os.path.exists(workshop_path):
                    sizes['workshop_size'] = self.get_folder_size_estimate(workshop_path)

                shader_path = os.path.join(steamapps_path, 'shadercache')
                if os.path.exists(shader_path):
                    sizes['shader_size'] = self.get_folder_size_estimate(shader_path)

            return sizes

        except Exception as e:
            logger.error(f"Error getting library sizes: {e}")
            return {
                'total_games_size': 0,
                'dlc_size': 0,
                'workshop_size': 0,
                'shader_size': 0,
            }

    def get_folder_size_estimate(self, folder_path, max_depth=2):
        """Get a quick size estimate by sampling"""
        try:
            total_size = 0
            count = 0
            max_samples = 50  # Limit for speed

            for root, dirs, files in os.walk(folder_path):
                if count >= max_samples:
                    break

                depth = root.replace(folder_path, '').count(os.sep)
                if depth >= max_depth:
                    dirs[:] = []  # Don't go deeper
                    continue

                for file in files[:10]:  # Sample first 10 files per directory
                    try:
                        file_path = os.path.join(root, file)
                        total_size += os.path.getsize(file_path)
                        count += 1
                    except:
                        continue

            return total_size
        except:
            return 0
