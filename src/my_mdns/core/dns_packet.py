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


def parse_mdns_packet(payload: bytes) -> tuple[
    str,
    tuple[tuple[str, str], ...],       # Queries (name, type)
    tuple[str, ...],
    list[tuple[str, str, bool]],          # A (name, ip, is_multicast)
    list[tuple[str, str, bool]],          # AAAA (name, ip, is_multicast)
    list[tuple[str, str, int, int, int]], # SRV
    list[tuple[str, str]],                # PTR
    list[tuple[str, str]],                # TXT
]:
    empty_res = ("Other", (), (), [], [], [], [], [])
    if len(payload) < 12:
        return empty_res

    try:
        _, flags, qdcount, ancount, _, _ = struct.unpack_from("!HHHHHH", payload, 0)
    except struct.error:
        return empty_res

    message_kind = "Response" if (flags & 0x8000) else "Query"
    offset = 12
    queries: list[tuple[str, str]] = []
    answer_types: list[str] = []
    a_records: list[tuple[str, str, bool]] = []
    aaaa_records: list[tuple[str, str, bool]] = []
    srv_records: list[tuple[str, str, int, int, int]] = []
    ptr_records: list[tuple[str, str]] = []
    txt_records: list[tuple[str, str]] = []

    for _ in range(qdcount):
        qname, _ = _read_name(payload, offset)
        offset = _skip_name(payload, offset)
        if offset + 4 > len(payload):
            return ("Other", tuple(queries), tuple(answer_types), a_records, aaaa_records, srv_records, ptr_records, txt_records)
        qtype = struct.unpack_from("!H", payload, offset)[0]
        queries.append((qname, _type_name(qtype)))
        offset += 4  # qtype + qclass

    for _ in range(ancount):
        name, _ = _read_name(payload, offset)
        offset = _skip_name(payload, offset)
        if offset + 10 > len(payload):
            return ("Other", tuple(queries), tuple(answer_types), a_records, aaaa_records, srv_records, ptr_records, txt_records)
        rtype, rclass, _, rdlength = struct.unpack_from("!HHIH", payload, offset)
        is_multicast = bool(rclass & 0x8000)
        answer_types.append(_type_name(rtype))
        offset += 10
        if offset + rdlength > len(payload):
            return ("Other", tuple(queries), tuple(answer_types), a_records, aaaa_records, srv_records, ptr_records, txt_records)
        
        if rtype == 1 and rdlength == 4: # A Record
            import socket
            ip_data = payload[offset : offset + 4]
            ip_str = socket.inet_ntoa(ip_data)
            a_records.append((name, ip_str, is_multicast))
        elif rtype == 28 and rdlength == 16: # AAAA Record
            import socket
            ip_data = payload[offset : offset + 16]
            ip_str = socket.inet_ntop(socket.AF_INET6, ip_data)
            aaaa_records.append((name, ip_str, is_multicast))
        elif rtype == 33 and rdlength >= 6: # SRV Record
            priority, weight, port = struct.unpack_from("!HHH", payload, offset)
            target, _ = _read_name(payload, offset + 6)
            srv_records.append((name, target, port, priority, weight))
        elif rtype == 12: # PTR Record
            ptrdname, _ = _read_name(payload, offset)
            ptr_records.append((name, ptrdname))
        elif rtype == 16: # TXT Record
            txt_offset = offset
            txt_end = offset + rdlength
            while txt_offset < txt_end:
                length = payload[txt_offset]
                txt_offset += 1
                if txt_offset + length > txt_end:
                    break
                text = payload[txt_offset : txt_offset + length].decode("utf-8", "replace")
                txt_records.append((name, text))
                txt_offset += length

        offset += rdlength

    return (message_kind, tuple(queries), tuple(answer_types), a_records, aaaa_records, srv_records, ptr_records, txt_records)
