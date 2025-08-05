from pathlib import Path
from typing import Any, Dict

from src.modules.sys_monitor.linux.read_file import read_file


def parse_meminfo(path: Path) -> Dict[str, Any]:
    meminfo = {}
    content = read_file(path)

    if not content:
        return meminfo

    for line in content.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            meminfo[key] = value.strip()

    return meminfo


if __name__ == "__main__":
    meminfo = parse_meminfo(Path("/proc/meminfo"))
    print(meminfo)
