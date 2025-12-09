# Disk I/O constants
DISK_SECTOR_SIZE = 512  # Bytes per sector
DEFAULT_IO_UPDATE_INTERVAL = 2.0  # Seconds between I/O stat updates
IO_TIME_MS_DIVISOR = 10.0  # Divisor for converting I/O time to seconds

# Monitoring
DEFAULT_MONITOR_UPDATE_INTERVAL = 2.0  # Seconds between system metric updates

# History buffer size (~2 minutes at 2s intervals)
HISTORY_SIZE = 60
