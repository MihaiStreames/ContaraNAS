from pathlib import Path
from typing import Dict, List

from ContaraNAS.core.utils import (get_cache_dir, get_logger, load_json,
                                   save_json)

logger = get_logger(__name__)

class SteamImageService:
    """Service for managing Steam game images"""
    # The idea is to manage downloading, caching, and retrieving game header images
    # They're stored within the DTOs (SteamGame.cover_url), but this service will handle
    # downloading and caching them locally for offline use and faster loading

    # The files would go into the cache directory, e.g.:
    # <cache_dir>/steam/images/<app_id>.jpg

    def __init__(self):
        self.image_cache: Dict[int, str] = {}  # app_id -> local_image_path
        self.image_cache_dir = get_cache_dir() / "steam" / "images"
