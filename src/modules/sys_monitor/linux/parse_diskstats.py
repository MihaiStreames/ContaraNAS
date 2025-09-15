from pathlib import Path
from typing import Any, Dict

from read_file import read_file


def parse_diskstats(path: Path, device_name: str) -> Dict[str, Any]:
    diskstats = {}
    content = read_file(path)

    if not content:
        return diskstats

    for line in content.splitlines():
        fields = line.split()
        if len(fields) >= 14 and fields[2] == device_name:
            diskstats["reads"] = int(fields[5])
            diskstats["writes"] = int(fields[9])
            diskstats["read_time"] = int(fields[6])
            diskstats["write_time"] = int(fields[10])
            diskstats["io_time"] = int(fields[12])

    return diskstats


if __name__ == "__main__":
    diskstats = parse_diskstats(Path("/proc/diskstats"), "nvme0n1")
    print(diskstats)
