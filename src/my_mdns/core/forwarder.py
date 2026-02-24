from __future__ import annotations

import socket


class MDNSForwarder:
    def __init__(self) -> None:
        self._targets: list[tuple[str, int]] = []
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

    def set_targets(self, targets: list[tuple[str, int]]) -> None:
        self._targets = targets

    def forward(self, payload: bytes) -> int:
        sent = 0
        for host, port in self._targets:
            self._sock.sendto(payload, (host, port))
            sent += 1
        return sent

    def close(self) -> None:
        self._sock.close()
