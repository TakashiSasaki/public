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
    def __init__(self, on_packet: Callable[[bytes, tuple[str, int]], Any]) -> None:
        self._on_packet = on_packet

    def datagram_received(self, data: bytes, addr: tuple[Any, ...]) -> None:
        host = str(addr[0])
        port = int(addr[1])
        self._on_packet(data, (host, port))


class MDNSCapture:
    def __init__(
        self,
        loop: asyncio.AbstractEventLoop,
        on_packet: Callable[[bytes, tuple[str, int]], Any],
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

        # IPv4 mDNS receive.
        try:
            sock_v4 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            sock_v4.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            if hasattr(socket, "SO_REUSEPORT"):
                try:
                    sock_v4.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
                except OSError:
                    pass
            sock_v4.bind(("", self._listen_port))

            ipv4_targets: list[str]
            if self._interface_ip != "0.0.0.0":
                ipv4_targets = [self._interface_ip]
            else:
                seen_v4: set[str] = set()
                ipv4_targets = []
                for interface in interfaces:
                    for addr in interface.ipv4_addresses:
                        if addr in seen_v4:
                            continue
                        seen_v4.add(addr)
                        ipv4_targets.append(addr)
                if not ipv4_targets:
                    ipv4_targets = ["0.0.0.0"]

            joined_v4 = 0
            for addr in ipv4_targets:
                try:
                    membership_v4 = socket.inet_aton(self._multicast_ip) + socket.inet_aton(addr)
                    sock_v4.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, membership_v4)
                    joined_v4 += 1
                except OSError as exc:
                    errors.append(f"ipv4 join {addr}: {exc}")

            if joined_v4 == 0:
                raise OSError("no ipv4 multicast group joined")
            sock_v4.setblocking(False)

            transport_v4, _ = await self._loop.create_datagram_endpoint(
                lambda: _CaptureProtocol(self._on_packet),
                sock=sock_v4,
            )
            self._transports.append(transport_v4)
            self._socks.append(sock_v4)
        except OSError as exc:
            errors.append(f"ipv4: {exc}")

        # IPv6 mDNS receive.
        try:
            sock_v6 = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            sock_v6.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            if hasattr(socket, "SO_REUSEPORT"):
                try:
                    sock_v6.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
                except OSError:
                    pass
            sock_v6.bind(("::", self._listen_port))

            seen_idx: set[int] = set()
            ipv6_if_indices: list[int] = []
            for interface in interfaces:
                if not interface.ipv6_addresses:
                    continue
                try:
                    idx = socket.if_nametoindex(interface.name)
                except OSError:
                    continue
                if idx in seen_idx:
                    continue
                seen_idx.add(idx)
                ipv6_if_indices.append(idx)
            if not ipv6_if_indices:
                ipv6_if_indices = [0]

            joined_v6 = 0
            for idx in ipv6_if_indices:
                try:
                    membership_v6 = socket.inet_pton(socket.AF_INET6, MDNS_MULTICAST_IPV6) + struct.pack("=I", idx)
                    sock_v6.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_JOIN_GROUP, membership_v6)
                    joined_v6 += 1
                except OSError as exc:
                    errors.append(f"ipv6 join ifindex={idx}: {exc}")

            if joined_v6 == 0:
                raise OSError("no ipv6 multicast group joined")
            sock_v6.setblocking(False)

            transport_v6, _ = await self._loop.create_datagram_endpoint(
                lambda: _CaptureProtocol(self._on_packet),
                sock=sock_v6,
            )
            self._transports.append(transport_v6)
            self._socks.append(sock_v6)
        except OSError as exc:
            errors.append(f"ipv6: {exc}")

        if not self._transports:
            raise OSError(f"failed to start mDNS capture ({'; '.join(errors)})")

    async def stop(self) -> None:
        for transport in self._transports:
            transport.close()
        self._transports.clear()
        for sock in self._socks:
            sock.close()
        self._socks.clear()
