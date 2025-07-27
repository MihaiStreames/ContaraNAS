from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class InterfaceInfo:
    bytes_sent: int
    bytes_recv: int
    packets_sent: int
    packets_recv: int
    errors_in: int
    errors_out: int
    drops_in: int
    drops_out: int
    send_speed_mbps: float
    recv_speed_mbps: float
    ipv4_address: Optional[str]
    ipv6_address: Optional[str]
    mac_address: Optional[str]
    is_up: bool
    speed_mbps: int
    mtu: int
    duplex: str
    type: str


@dataclass
class WifiInfo:
    ssid: str = "N/A"
    security: str = "N/A"
    signal_strength: str = "N/A"
    quality: Optional[str] = None


@dataclass
class NetworkInfo:
    interfaces: Dict[str, InterfaceInfo]
    hostname: str
    fqdn: str
    active_connections: int
    wifi_info: WifiInfo
    default_gateway: str
    routing_table_entries: int
