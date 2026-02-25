from __future__ import annotations

import asyncio
import socket
import struct
from collections.abc import Callable
from typing import Any


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

            membership_v4 = socket.inet_aton(self._multicast_ip) + socket.inet_aton(self._interface_ip)
            sock_v4.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, membership_v4)
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

            membership_v6 = socket.inet_pton(socket.AF_INET6, MDNS_MULTICAST_IPV6) + struct.pack("=I", 0)
            sock_v6.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_JOIN_GROUP, membership_v6)
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
