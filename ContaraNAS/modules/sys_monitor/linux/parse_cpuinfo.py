from pathlib import Path
from typing import Any

from read_file import read_file


def parse_cpuinfo(path: Path) -> dict[str, Any]:
    cpuinfo = {}
    content = read_file(path)

    if not content:
        return cpuinfo

    for line in content.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            cpuinfo[key] = value.strip()

    return cpuinfo


if __name__ == "__main__":
    cpuinfo = parse_cpuinfo(Path("/proc/cpuinfo"))
    print(cpuinfo)
