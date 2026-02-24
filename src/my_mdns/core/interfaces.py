from __future__ import annotations

import socket


def list_interfaces() -> list[str]:
    try:
        names = [name for _, name in socket.if_nameindex()]
    except OSError:
        names = []

    if not names:
        return ["all (0.0.0.0)"]

    # Keep order stable and avoid duplicates.
    deduped: list[str] = []
    seen: set[str] = set()
    for name in names:
        if name in seen:
            continue
        seen.add(name)
        deduped.append(name)
    return deduped
