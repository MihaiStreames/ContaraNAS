"""Steam module constants"""

# Image service constants
MIN_VALID_IMAGE_SIZE = 1000  # Minimum bytes for a valid image file
IMAGE_DOWNLOAD_DELAY = 0.1   # Seconds to wait between image downloads
HTTP_RETRY_COUNT = 3         # Number of retries for HTTP requests
HTTP_TIMEOUT_SECONDS = 10    # HTTP request timeout in seconds

# Monitoring service constants
OBSERVER_JOIN_TIMEOUT = 5.0  # Seconds to wait for observer thread to finish

# Game library modal constants
SORT_BY_SIZE = "size"
SORT_BY_NAME = "name"
SORT_BY_LAST_PLAYED = "last_played"

SORT_OPTIONS = {
    SORT_BY_SIZE: "Size",
    SORT_BY_NAME: "Name",
    SORT_BY_LAST_PLAYED: "Last Played"
}
