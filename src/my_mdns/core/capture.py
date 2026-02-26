from __future__ import annotations

import asyncio
import socket
import struct
from collections.abc import Callable
from typing import Any

from my_mdns.core.interfaces import list_interfaces


MDNS_MULTICAST_IP = "224.0.0.251"
MDNS_MULTICAST_IPV6 = "ff02::fb"
MDNS_PORT = 5353


class _CaptureProtocol(asyncio.DatagramProtocol):
    def __init__(
        self,
        on_packet: Callable[[bytes, tuple[str, int], str, str], Any],
        capture_interface: str,
        address_family: str,
    ) -> None:
        self._on_packet = on_packet
        self._capture_interface = capture_interface
        self._address_family = address_family

    def datagram_received(self, data: bytes, addr: tuple[Any, ...]) -> None:
        host = str(addr[0])
        port = int(addr[1])
        self._on_packet(data, (host, port), self._capture_interface, self._address_family)


class MDNSCapture:
    def __init__(
        self,
        loop: asyncio.AbstractEventLoop,
        on_packet: Callable[[bytes, tuple[str, int], str, str], Any],
        listen_port: int = MDNS_PORT,
        multicast_ip: str = MDNS_MULTICAST_IP,
        interface_ip: str = "0.0.0.0",
    ) -> None:
        self._loop = loop
        self._on_packet = on_packet
        self._listen_port = listen_port
        self._multicast_ip = multicast_ip
        self._interface_ip = interface_ip
        self._transports: list[asyncio.DatagramTransport] = []
        self._socks: list[socket.socket] = []

    async def start(self) -> None:
        if self._transports:
            return

        errors: list[str] = []
        interfaces = list_interfaces()

        # IPv4 mDNS receive: single socket for all interfaces
        try:
            sock_v4 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            sock_v4.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            if hasattr(socket, "SO_REUSEPORT"):
                try:
                    sock_v4.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
                except OSError:
                    pass
            
            # Bind to all interfaces
            sock_v4.bind(("", self._listen_port))
            
            joined_any_v4 = False
            for interface in interfaces:
                if self._interface_ip != "0.0.0.0":
                    if self._interface_ip not in interface.ipv4_addresses:
                        continue
                    target_ipv4s = [self._interface_ip]
                else:
                    target_ipv4s = interface.ipv4_addresses

                for addr in target_ipv4s:
                    try:
                        membership_v4 = socket.inet_aton(self._multicast_ip) + socket.inet_aton(addr)
                        sock_v4.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, membership_v4)
                        joined_any_v4 = True
                    except OSError as exc:
                        errors.append(f"ipv4 join fail if={interface.name} addr={addr}: {exc}")

            if joined_any_v4:
                sock_v4.setblocking(False)
                transport_v4, _ = await self._loop.create_datagram_endpoint(
                    lambda: _CaptureProtocol(self._on_packet, "IPv4", "IPv4"),
                    sock=sock_v4,
                )
                self._transports.append(transport_v4)
                self._socks.append(sock_v4)
            else:
                sock_v4.close()
        except OSError as exc:
            errors.append(f"ipv4 socket setup failed: {exc}")

        # IPv6 mDNS receive: single socket for all interfaces
        try:
            sock_v6 = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            sock_v6.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            if hasattr(socket, "SO_REUSEPORT"):
                try:
                    sock_v6.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
                except OSError:
                    pass
            
            # Bind to all interfaces
            sock_v6.bind(("::", self._listen_port))
            
            joined_any_v6 = False
            for interface in interfaces:
                if not interface.ipv6_addresses:
                    continue
                try:
                    idx = socket.if_nametoindex(interface.name)
                except OSError:
                    continue
                    
                try:
                    membership_v6 = socket.inet_pton(socket.AF_INET6, MDNS_MULTICAST_IPV6) + struct.pack("=I", idx)
                    sock_v6.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_JOIN_GROUP, membership_v6)
                    joined_any_v6 = True
                except OSError as exc:
                    errors.append(f"ipv6 join fail if={interface.name} idx={idx}: {exc}")

            if joined_any_v6:
                sock_v6.setblocking(False)
                transport_v6, _ = await self._loop.create_datagram_endpoint(
                    lambda: _CaptureProtocol(self._on_packet, "IPv6", "IPv6"),
                    sock=sock_v6,
                )
                self._transports.append(transport_v6)
                self._socks.append(sock_v6)
            else:
                sock_v6.close()
        except OSError as exc:
            errors.append(f"ipv6 socket setup failed: {exc}")

        if not self._transports:
            raise OSError(f"failed to start mDNS capture ({'; '.join(errors)})")

    async def stop(self) -> None:
        for transport in self._transports:
            transport.close()
        self._transports.clear()
        for sock in self._socks:
            sock.close()
        self._socks.clear()
