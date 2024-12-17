import os
import vdf

from utils import load_json, save_json, SteamDBScraper, format_size, get_size, check_url, parse_output, get_logger

logger = get_logger(__name__)


class SteamGame:
    def __init__(self, app_id, name, library_path, cache_dir):
        self.app_id = app_id
        self.name = name
        self.library_path = library_path
        self.cache_dir = cache_dir
        self.manifest_path = os.path.join(library_path, 'steamapps', f"appmanifest_{app_id}.acf")
        self.cache_path = os.path.join(cache_dir, f"{app_id}.json")
        self.depot_cache_path = os.path.join(cache_dir, 'depots', f"{app_id}_depots.json")

        # Attributes to be filled during loading
        self.cover_image_url = f"https://steamcdn-a.akamaihd.net/steam/apps/{app_id}/header.jpg"
        self.store_page_url = None
        self.size_on_disk = "0 B"
        self.dlc_size = "0 B"
        self.shader_cache_size = "0 B"
        self.workshop_content_size = "0 B"
        self.depots = {}

        self.scraper = SteamDBScraper()

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
        self.size_on_disk = data.get("size_on_disk", "0 B")
        self.dlc_size = data.get("dlc_size", "0 B")
        self.shader_cache_size = data.get("shader_cache_size", "0 B")
        self.workshop_content_size = data.get("workshop_content_size", "0 B")
        self.depots = data.get("depots", {})

    def load_from_manifest(self):
        if not os.path.exists(self.manifest_path):
            logger.warning(f"Manifest file not found for App ID {self.app_id}")
            return

        logger.info(f"Loading manifest for {self.name} (AppID: {self.app_id})")

        with open(self.manifest_path, 'r', encoding='utf-8') as f:
            acf_data = vdf.load(f).get('AppState', {})
            self.size_on_disk = format_size(int(acf_data.get('SizeOnDisk', 0)))
            self.store_page_url = self._get_store_page_url()
            self._load_shader_cache_size()
            self._load_workshop_content_size()

            # Initialize depots from the manifest without scraping (just IDs and sizes)
            self._load_depot_ids_from_manifest(acf_data)

    def _load_shader_cache_size(self):
        logger.debug(f"Calculating shader cache size for {self.name} (AppID: {self.app_id})")

        shader_cache_path = os.path.join(self.library_path, 'steamapps', 'shadercache', self.app_id)
        self.shader_cache_size = format_size(get_size(shader_cache_path) if os.path.exists(shader_cache_path) else 0)

    def _load_workshop_content_size(self):
        logger.debug(f"Calculating workshop content size for {self.name} (AppID: {self.app_id})")

        workshop_content_path = os.path.join(self.library_path, 'steamapps', 'workshop', 'content', self.app_id)
        self.workshop_content_size = format_size(get_size(workshop_content_path) if os.path.exists(workshop_content_path) else 0)

    def _load_depot_ids_from_manifest(self, acf_data):
        installed_depots = acf_data.get('InstalledDepots', {})
        # Just store depots as ID => size for now
        # Details will be fetched only if needed when update_depots() is called
        basic_depots = {}
        dlc_size_total = 0

        for depot_id, depot_data in installed_depots.items():
            depot_size = int(depot_data.get('size', 0))
            dlc_id = depot_data.get('dlcappid')
            # Store a placeholder name, since we haven't scraped yet
            if dlc_id:
                basic_depots[f"(DLC ID {dlc_id}) (DEPOT ID {depot_id})"] = format_size(depot_size)
                dlc_size_total += depot_size
            else:
                basic_depots[f"(DEPOT ID {depot_id})"] = format_size(depot_size)

        self.depots = basic_depots
        self.dlc_size = format_size(dlc_size_total)

    def has_new_depots(self):
        depot_data = load_json(self.depot_cache_path)

        if depot_data is None:
            logger.debug(f"No depot cache for {self.name} (AppID: {self.app_id}), needs scraping.")
            return True

        manifest_depot_ids = self._get_manifest_depot_ids()
        cached_depot_ids = {depot['depot_id'] for depot in depot_data.get('depots', [])}

        if not manifest_depot_ids.issubset(cached_depot_ids):
            logger.debug(
                f"New depots found for {self.name} (AppID: {self.app_id}). "
                f"Manifest depots: {manifest_depot_ids}, Cached depots: {cached_depot_ids}"
            )
            return True
        else:
            logger.debug(f"No new depots for {self.name} (AppID: {self.app_id}). Skipping scrape.")
            return False

    def _get_manifest_depot_ids(self):
        if not os.path.exists(self.manifest_path):
            return set()

        with open(self.manifest_path, 'r', encoding='utf-8') as f:
            acf_data = vdf.load(f).get('AppState', {})
            installed_depots = acf_data.get('InstalledDepots', {})
            return set(installed_depots.keys())

    def update_depots(self):
        logger.debug(f"Updating depots for {self.name} (AppID: {self.app_id})")
        # Attempt to scrape
        try:
            depot_details = self.scraper.get_game_details(self.app_id)
            if depot_details is None:
                raise Exception("No depot details returned.")
            rate_limited = False
            logger.debug(f"Depot details fetched successfully for {self.app_id}")

        except Exception as e:
            logger.warning(f"Failed to fetch depots for {self.app_id}: {e}")
            depot_details = {"dlc": [], "depots": []}
            rate_limited = True

        # Re-build depots using the newly fetched or fallback logic
        with open(self.manifest_path, 'r', encoding='utf-8') as f:
            acf_data = vdf.load(f).get('AppState', {})
            installed_depots = acf_data.get('InstalledDepots', {})

        dlc_size_total = 0
        depots_info = {}

        for depot_id, depot_data in installed_depots.items():
            depot_size = int(depot_data.get('size', 0))
            dlc_id = depot_data.get('dlcappid')

            if rate_limited:
                # Fallback case
                if dlc_id:
                    depots_info[f"(DLC ID {dlc_id}) (DEPOT ID {depot_id})"] = format_size(depot_size)
                    dlc_size_total += depot_size
                else:
                    depots_info[f"(DEPOT ID {depot_id})"] = format_size(depot_size)
            else:
                # Use parsed depot details from SteamDB
                depot_details.get('depots', [])
                # parse_output should find a matching depot entry by id
                depot_name = parse_output(depot_id, depot_details)
                formatted_depot_name = f"({depot_id}) {depot_name}"

                if dlc_id:
                    dlc_name = parse_output(dlc_id, depot_details)
                    depots_info[f"({depot_id}) {dlc_name}"] = format_size(depot_size)
                    dlc_size_total += depot_size
                else:
                    depots_info[formatted_depot_name] = format_size(depot_size)

        self.dlc_size = format_size(dlc_size_total)
        self.depots = depots_info

        # Save updated depot details if not rate-limited
        if not rate_limited:
            depot_cache_dir = os.path.dirname(self.depot_cache_path)
            os.makedirs(depot_cache_dir, exist_ok=True)
            save_json(self.depot_cache_path, depot_details)

    def _get_store_page_url(self):
        url = f"https://store.steampowered.com/app/{self.app_id}/"
        return url if check_url(url) else None

    def quick_size_check(self):
        if not os.path.exists(self.manifest_path):
            return "N/A"

        with open(self.manifest_path, 'r', encoding='utf-8') as f:
            data = vdf.load(f).get('AppState', {})
            return format_size(int(data.get('SizeOnDisk', 0)))

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