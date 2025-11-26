"""Steam module constants"""

# Steam directory paths
STEAMAPPS_DIR = "steamapps"
SHADERCACHE_DIR = "shadercache"
WORKSHOP_DIR = "workshop"
WORKSHOP_CONTENT_DIR = "content"
COMMON_DIR = "common"

# Steam files
LIBRARY_FOLDERS_FILE = "libraryfolders.vdf"
APP_MANIFEST_PATTERN = "appmanifest_*.acf"
APP_MANIFEST_PREFIX = "appmanifest_"
APP_MANIFEST_SUFFIX = ".acf"

# Cache paths
IMAGE_CACHE_DIR = "images"

# Image service constants
MIN_VALID_IMAGE_SIZE = 1000  # Minimum bytes for a valid image file
IMAGE_DOWNLOAD_DELAY = 0.1  # Seconds to wait between image downloads
HTTP_RETRY_COUNT = 3  # Number of retries for HTTP requests
HTTP_TIMEOUT_SECONDS = 10  # HTTP request timeout in seconds

# Monitoring service constants
OBSERVER_JOIN_TIMEOUT = 5.0  # Seconds to wait for observer thread to finish
