from __future__ import annotations

import asyncio
import socket
from collections.abc import Callable
from typing import Any


MDNS_MULTICAST_IP = "224.0.0.251"
MDNS_PORT = 5353


class _CaptureProtocol(asyncio.DatagramProtocol):
    def __init__(self, on_packet: Callable[[bytes, tuple[str, int]], Any]) -> None:
        self._on_packet = on_packet

    def datagram_received(self, data: bytes, addr: tuple[str, int]) -> None:
        self._on_packet(data, addr)


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
        self._transport: asyncio.DatagramTransport | None = None
        self._sock: socket.socket | None = None

    async def start(self) -> None:
        if self._transport is not None:
            return

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("", self._listen_port))

        membership = socket.inet_aton(self._multicast_ip) + socket.inet_aton(self._interface_ip)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, membership)
        sock.setblocking(False)

        transport, _ = await self._loop.create_datagram_endpoint(
            lambda: _CaptureProtocol(self._on_packet),
            sock=sock,
        )
        self._transport = transport
        self._sock = sock

    async def stop(self) -> None:
        if self._transport is not None:
            self._transport.close()
            self._transport = None
        if self._sock is not None:
            self._sock.close()
            self._sock = None
