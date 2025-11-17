"""System Monitor module constants"""

# Disk I/O constants
DISK_SECTOR_SIZE = 512            # Bytes per sector
DEFAULT_IO_UPDATE_INTERVAL = 2.0  # Seconds between I/O stat updates
IO_TIME_MS_DIVISOR = 10.0         # Divisor for converting I/O time to seconds

# GUI display constants
MAX_HISTORY_POINTS = 30  # Maximum number of data points to keep in history graphs
MAX_DISPLAYED_DISKS = 3  # Maximum number of disks to show before "show more"

# Graph dimensions (pixels)
CPU_GRAPH_HEIGHT = 100
MEMORY_GRAPH_HEIGHT = 80
PER_CORE_GRAPH_HEIGHT = 50
MAX_GRID_COLUMNS = 4  # Maximum columns in per-core CPU grid
