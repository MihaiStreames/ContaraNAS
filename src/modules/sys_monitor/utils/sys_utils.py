import re


def get_physical_device_name(device_path: str) -> str:
    """Get the physical device name from partition path"""
    # Handle NVMe devices: /dev/nvme0n1p1 -> nvme0n1
    if "nvme" in device_path:
        match = re.match(r"/dev/(nvme\d+n\d+)", device_path)
        return match.group(1) if match else device_path.split("/")[-1]

    # Handle SATA/SCSI devices: /dev/sda1 -> sda
    match = re.match(r"/dev/([a-z]+)", device_path)
    return match.group(1) if match else device_path.split("/")[-1]


def determine_interface_type(interface: str) -> str:
    """Determine network interface type from name"""
    if interface.startswith("wlan") or interface.startswith("wifi"):
        return "WiFi"
    elif (
        interface.startswith("eth")
        or interface.startswith("eno")
        or interface.startswith("enp")
    ):
        return "Ethernet"
    elif interface.startswith("wwan") or interface.startswith("ppp"):
        return "Mobile/Cellular"
    elif interface.startswith("lo"):
        return "Loopback"
    elif interface.startswith(("docker", "br-", "veth")):
        return "Virtual"
    else:
        return "Unknown"
