from __future__ import annotations

import struct


TYPE_NAMES = {
    1: "A",
    12: "PTR",
    16: "TXT",
    28: "AAAA",
    33: "SRV",
    255: "ANY",
}


def _type_name(value: int) -> str:
    return TYPE_NAMES.get(value, f"TYPE{value}")


def _skip_name(payload: bytes, offset: int) -> int:
    limit = len(payload)
    while offset < limit:
        length = payload[offset]
        offset += 1
        if length == 0:
            return offset
        if (length & 0xC0) == 0xC0:
            if offset >= limit:
                return limit
            return offset + 1
        offset += length
    return limit


def _read_name(payload: bytes, offset: int, depth: int = 0) -> tuple[str, int]:
    if depth > 10:  # Prevent infinite loops in malformed packets
        return "", offset
    
    parts = []
    limit = len(payload)
    original_offset = offset

    while offset < limit:
        length = payload[offset]
        if length == 0:
            offset += 1
            break
        if (length & 0xC0) == 0xC0:
            if offset + 1 >= limit:
                break
            # Pointer
            ptr_offset = ((length & 0x3F) << 8) | payload[offset + 1]
            ptr_name, _ = _read_name(payload, ptr_offset, depth + 1)
            if ptr_name:
                parts.append(ptr_name)
            offset += 2
            break
        else:
            offset += 1
            if offset + length > limit:
                break
            parts.append(payload[offset : offset + length].decode("utf-8", "replace"))
            offset += length

    return ".".join(parts), offset


def parse_mdns_packet(payload: bytes) -> tuple[str, tuple[str, ...], tuple[str, ...], list[tuple[str, str]]]:
    if len(payload) < 12:
        return ("Other", (), (), [])

    try:
        _, flags, qdcount, ancount, _, _ = struct.unpack_from("!HHHHHH", payload, 0)
    except struct.error:
        return ("Other", (), (), [])

    message_kind = "Response" if (flags & 0x8000) else "Query"
    offset = 12
    query_types: list[str] = []
    answer_types: list[str] = []
    a_records: list[tuple[str, str]] = []

    for _ in range(qdcount):
        offset = _skip_name(payload, offset)
        if offset + 4 > len(payload):
            return ("Other", tuple(query_types), tuple(answer_types), a_records)
        qtype = struct.unpack_from("!H", payload, offset)[0]
        query_types.append(_type_name(qtype))
        offset += 4  # qtype + qclass

    for _ in range(ancount):
        name, _ = _read_name(payload, offset)
        offset = _skip_name(payload, offset)
        if offset + 10 > len(payload):
            return ("Other", tuple(query_types), tuple(answer_types), a_records)
        rtype, _, _, rdlength = struct.unpack_from("!HHIH", payload, offset)
        answer_types.append(_type_name(rtype))
        offset += 10
        if offset + rdlength > len(payload):
            return ("Other", tuple(query_types), tuple(answer_types), a_records)
        
        if rtype == 1 and rdlength == 4: # A Record
            import socket
            ip_data = payload[offset : offset + 4]
            ip_str = socket.inet_ntoa(ip_data)
            a_records.append((name, ip_str))

        offset += rdlength

    return (message_kind, tuple(query_types), tuple(answer_types), a_records)
