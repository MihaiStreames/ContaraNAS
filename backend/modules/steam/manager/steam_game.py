import os

import vdf

from backend.core.utils import load_json, save_json, get_logger
from ..utils.steam_helpers import format_size, get_size, check_url

logger = get_logger(__name__)


class SteamGame:
    def __init__(self, app_id, name, library_path, cache_dir):
        self.app_id = app_id
        self.name = name
        self.library_path = library_path
        self.cache_dir = cache_dir
        self.manifest_path = os.path.join(library_path, 'steamapps', f"appmanifest_{app_id}.acf")
        self.cache_path = os.path.join(cache_dir, f"{app_id}.json")

        # Attributes to be filled during loading
        self.cover_image_url = f"https://steamcdn-a.akamaihd.net/steam/apps/{app_id}/header.jpg"
        self.store_page_url = None
        self.size_on_disk = 0
        self.dlc_size = 0
        self.shader_cache_size = 0
        self.workshop_content_size = 0
        self.depots = {}

        if not self.load_from_cache():
            self.load_from_manifest()
            self.save_to_cache()

    def load_from_cache(self):
        data = load_json(self.cache_path)

        if not data:
            logger.debug(f"No cache found for {self.name} (AppID: {self.app_id}), loading from manifest.")
            return False
        else:
            logger.debug(f"Cache found for {self.name} (AppID: {self.app_id}). Using cached data.")
            self._load_attrs_from_data(data)
            return True

    def _load_attrs_from_data(self, data):
        self.cover_image_url = data.get("cover_image_url", self.cover_image_url)
        self.store_page_url = data.get("store_page_url", self._get_store_page_url())
        self.size_on_disk = data.get("size_on_disk", 0)
        self.dlc_size = data.get("dlc_size", 0)
        self.shader_cache_size = data.get("shader_cache_size", 0)
        self.workshop_content_size = data.get("workshop_content_size", 0)
        self.depots = data.get("depots", {})

    def load_from_manifest(self):
        if not os.path.exists(self.manifest_path):
            logger.warning(f"Manifest file not found for App ID {self.app_id}")
            return

        logger.info(f"Loading manifest for {self.name} (AppID: {self.app_id})")

        with open(self.manifest_path, 'r', encoding='utf-8') as f:
            acf_data = vdf.load(f).get('AppState', {})
            self.size_on_disk = int(acf_data.get('SizeOnDisk', 0))
            self.store_page_url = self._get_store_page_url()
            self._load_shader_cache_size()
            self._load_workshop_content_size()
            self._load_depots_from_manifest(acf_data)

    def _load_shader_cache_size(self):
        logger.debug(f"Calculating shader cache size for {self.name} (AppID: {self.app_id})")

        shader_cache_path = os.path.join(self.library_path, 'steamapps', 'shadercache', self.app_id)
        self.shader_cache_size = get_size(shader_cache_path) if os.path.exists(shader_cache_path) else 0

    def _load_workshop_content_size(self):
        logger.debug(f"Calculating workshop content size for {self.name} (AppID: {self.app_id})")

        workshop_content_path = os.path.join(self.library_path, 'steamapps', 'workshop', 'content', self.app_id)
        self.workshop_content_size = get_size(workshop_content_path) if os.path.exists(workshop_content_path) else 0

    def _load_depots_from_manifest(self, acf_data):
        installed_depots = acf_data.get('InstalledDepots', {})
        depots_info = {}
        dlc_size_total = 0

        for depot_id, depot_data in installed_depots.items():
            depot_size = int(depot_data.get('size', 0))
            dlc_id = depot_data.get('dlcappid')

            if dlc_id:
                # DLC depot: show as "DLC_ID: DEPOT_ID"
                depot_name = f"{dlc_id}: {depot_id}"
                dlc_size_total += depot_size
            else:
                # Main game depot: show as "GAME_ID: DEPOT_ID"
                depot_name = f"{self.app_id}: {depot_id}"

            depots_info[depot_name] = format_size(depot_size)

        self.depots = depots_info
        self.dlc_size = dlc_size_total

    def has_new_depots(self):
        """Check if manifest has been updated since last cache"""
        if not os.path.exists(self.manifest_path):
            return False

        # Simple check: if manifest is newer than cache, reload
        cache_exists = os.path.exists(self.cache_path)
        if not cache_exists:
            return True

        manifest_mtime = os.path.getmtime(self.manifest_path)
        cache_mtime = os.path.getmtime(self.cache_path)

        return manifest_mtime > cache_mtime

    def update_depots(self):
        """Update depot information from manifest"""
        logger.debug(f"Updating depots for {self.name} (AppID: {self.app_id})")

        if not os.path.exists(self.manifest_path):
            logger.warning(f"Manifest file not found for App ID {self.app_id}")
            return

        with open(self.manifest_path, 'r', encoding='utf-8') as f:
            acf_data = vdf.load(f).get('AppState', {})
            self._load_depots_from_manifest(acf_data)

    def _get_store_page_url(self):
        url = f"https://store.steampowered.com/app/{self.app_id}/"
        return url if check_url(url) else None

    def save_to_cache(self):
        data = {
            "app_id": self.app_id,
            "name": self.name,
            "location": self.library_path,
            "cover_image_url": self.cover_image_url,
            "store_page_url": self.store_page_url,
            "size_on_disk": self.size_on_disk,
            "dlc_size": self.dlc_size,
            "shader_cache_size": self.shader_cache_size,
            "workshop_content_size": self.workshop_content_size,
            "depots": self.depots,
        }

        save_json(self.cache_path, data)

    # Convenience methods for formatted display
    def get_formatted_size_on_disk(self):
        return format_size(self.size_on_disk)

    def get_formatted_dlc_size(self):
        return format_size(self.dlc_size)

    def get_formatted_shader_cache_size(self):
        return format_size(self.shader_cache_size)

    def get_formatted_workshop_content_size(self):
        return format_size(self.workshop_content_size)

    def get_total_size(self):
        """Get total size including all components"""
        return self.size_on_disk + self.dlc_size + self.shader_cache_size + self.workshop_content_size
