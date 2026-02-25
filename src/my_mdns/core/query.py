from __future__ import annotations

import socket
import struct


MDNS_IPV4_GROUP = "224.0.0.251"
MDNS_IPV6_GROUP = "ff02::fb"
MDNS_PORT = 5353
QTYPE_MAP = {
    "A": 1,
    "PTR": 12,
    "TXT": 16,
    "AAAA": 28,
    "SRV": 33,
}


def _encode_dns_name(name: str) -> bytes:
    labels = [label for label in name.rstrip(".").split(".") if label]
    encoded = bytearray()
    for label in labels:
        label_bytes = label.encode("utf-8")
        if len(label_bytes) > 63:
            raise ValueError(f"DNS label too long: {label}")
        encoded.append(len(label_bytes))
        encoded.extend(label_bytes)
    encoded.append(0)
    return bytes(encoded)


def build_services_ptr_query() -> bytes:
    # Standard DNS query header:
    # ID=0, FLAGS=0x0000, QDCOUNT=1, ANCOUNT=0, NSCOUNT=0, ARCOUNT=0
    header = struct.pack("!HHHHHH", 0, 0, 1, 0, 0, 0)
    qname = _encode_dns_name("_services._dns-sd._udp.local.")
    question = struct.pack("!HH", 12, 1)  # QTYPE=PTR, QCLASS=IN
    return header + qname + question


def build_query(qname: str, qtype_name: str) -> bytes:
    qtype = QTYPE_MAP.get(qtype_name.upper())
    if qtype is None:
        raise ValueError(f"unsupported qtype: {qtype_name}")

    header = struct.pack("!HHHHHH", 0, 0, 1, 0, 0, 0)
    encoded_name = _encode_dns_name(qname)
    question = struct.pack("!HH", qtype, 1)  # QCLASS=IN
    return header + encoded_name + question


def send_mdns_query_ipv4(interface_ip: str, payload: bytes) -> None:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    try:
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(interface_ip))
        sock.sendto(payload, (MDNS_IPV4_GROUP, MDNS_PORT))
    finally:
        sock.close()


def send_mdns_query_ipv6(interface_index: int, payload: bytes) -> None:
    sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    try:
        sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_MULTICAST_IF, interface_index)
        sock.sendto(payload, (MDNS_IPV6_GROUP, MDNS_PORT, 0, interface_index))
    finally:
        sock.close()
