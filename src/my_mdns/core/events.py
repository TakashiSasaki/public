from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class PacketEvent:
    timestamp: datetime
    source_host: str
    source_port: int
    capture_interface: str
    address_family: str
    message_kind: str
    query_types: tuple[str, ...]
    answer_types: tuple[str, ...]
    byte_count: int
    preview_hex: str
    forwarded_count: int


@dataclass(slots=True)
class LogEvent:
    timestamp: datetime
    level: str
    message: str


@dataclass(slots=True)
class ARecordEvent:
    name: str
    ip: str
    last_seen: str
    source_ip: str


@dataclass(slots=True)
class AAAARecordEvent:
    name: str
    ip: str
    last_seen: str
    source_ip: str


@dataclass(slots=True)
class SRVRecordEvent:
    name: str
    target: str
    port: int
    priority: int
    weight: int
    last_seen: str
    source_ip: str


@dataclass(slots=True)
class PTRRecordEvent:
    name: str
    ptrdname: str
    last_seen: str
    source_ip: str


@dataclass(slots=True)
class TXTRecordEvent:
    name: str
    text: str
    last_seen: str
    source_ip: str
