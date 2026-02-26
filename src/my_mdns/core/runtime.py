from __future__ import annotations

import asyncio
import socket
import threading
from datetime import datetime
from queue import Queue

from my_mdns.core.capture import MDNSCapture
from my_mdns.core.dns_packet import parse_mdns_packet
from my_mdns.core.events import ARecordEvent, LogEvent, PacketEvent
from my_mdns.core.forwarder import MDNSForwarder
from my_mdns.core.query import build_query, build_services_ptr_query, send_mdns_query_ipv4, send_mdns_query_ipv6
from my_mdns.core import store



class CoreRuntime:
    def __init__(self, event_queue: Queue[PacketEvent | LogEvent]) -> None:
        self._event_queue = event_queue
        self._loop: asyncio.AbstractEventLoop | None = None
        self._thread: threading.Thread | None = None
        self._capture: MDNSCapture | None = None
        self._forwarder: MDNSForwarder | None = None
        self._loop_ready = threading.Event()
        self._targets: list[tuple[str, int]] = []
        self._running = False

    def start(self) -> None:
        if self._running:
            return
        self._loop = asyncio.new_event_loop()
        self._capture = MDNSCapture(self._loop, self._on_packet)
        self._forwarder = MDNSForwarder()
        self._forwarder.set_targets(self._targets)
        self._loop_ready.clear()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._running = True
        self._thread.start()
        self._loop_ready.wait(timeout=3)
        asyncio.run_coroutine_threadsafe(self._capture.start(), self._loop).result(timeout=3)
        self._log("INFO", "mDNS capture started")

    def stop(self) -> None:
        if not self._running:
            return
        try:
            if self._loop is not None and self._capture is not None:
                asyncio.run_coroutine_threadsafe(self._capture.stop(), self._loop).result(timeout=3)
        finally:
            if self._forwarder is not None:
                self._forwarder.close()
            if self._loop is not None:
                self._loop.call_soon_threadsafe(self._loop.stop)
            if self._thread is not None:
                self._thread.join(timeout=3)
            self._capture = None
            self._forwarder = None
            self._thread = None
            self._loop = None
            self._running = False
            self._log("INFO", "mDNS capture stopped")

    def set_forward_target(self, host: str, port: int) -> None:
        self._targets = [(host, port)]
        if self._forwarder is not None:
            self._forwarder.set_targets(self._targets)
        self._log("INFO", f"forward target set to {host}:{port}")

    def clear_forward_target(self) -> None:
        self._targets = []
        if self._forwarder is not None:
            self._forwarder.set_targets([])
        self._log("INFO", "forward target disabled")

    def send_service_query_ipv4(self, interface_ip: str) -> None:
        payload = build_services_ptr_query()
        try:
            send_mdns_query_ipv4(interface_ip, payload)
            self._log("INFO", f"sent mDNS services query via IPv4 on {interface_ip}")
        except OSError as exc:
            self._log("ERROR", f"failed to send mDNS services query via IPv4 on {interface_ip}: {exc}")
            raise

    def send_service_query_ipv6(self, interface_name: str) -> None:
        payload = build_services_ptr_query()
        try:
            interface_index = socket.if_nametoindex(interface_name)
            send_mdns_query_ipv6(interface_index, payload)
            self._log("INFO", f"sent mDNS services query via IPv6 on {interface_name}")
        except OSError as exc:
            self._log("ERROR", f"failed to send mDNS services query via IPv6 on {interface_name}: {exc}")
            raise

    def send_manual_query_ipv4(self, interface_ip: str, qname: str, qtype_name: str) -> None:
        try:
            payload = build_query(qname, qtype_name)
            send_mdns_query_ipv4(interface_ip, payload)
            self._log("INFO", f"sent mDNS query via IPv4 on {interface_ip}: {qname} {qtype_name.upper()}")
        except (OSError, ValueError) as exc:
            self._log("ERROR", f"failed to send mDNS query via IPv4 on {interface_ip}: {exc}")
            raise

    def send_manual_query_ipv6(self, interface_name: str, qname: str, qtype_name: str) -> None:
        try:
            payload = build_query(qname, qtype_name)
            interface_index = socket.if_nametoindex(interface_name)
            send_mdns_query_ipv6(interface_index, payload)
            self._log("INFO", f"sent mDNS query via IPv6 on {interface_name}: {qname} {qtype_name.upper()}")
        except (OSError, ValueError) as exc:
            self._log("ERROR", f"failed to send mDNS query via IPv6 on {interface_name}: {exc}")
            raise

    def _run_loop(self) -> None:
        if self._loop is None:
            return
        asyncio.set_event_loop(self._loop)
        self._loop_ready.set()
        self._loop.run_forever()

    def _on_packet(self, payload: bytes, addr: tuple[str, int], capture_interface: str, address_family: str) -> None:
        forwarded = 0
        try:
            if self._forwarder is not None:
                forwarded = self._forwarder.forward(payload)
        except OSError as exc:
            self._log("ERROR", f"forward error: {exc}")
        message_kind, query_types, answer_types, a_records = parse_mdns_packet(payload)

        # Store A records and notify GUI
        for name, ip in a_records:
            try:
                store.add_a_record(name, ip)
                self._event_queue.put(ARecordEvent(name=name, ip=ip))
            except Exception as e:
                self._log("ERROR", f"failed to store A record: {e}")

        self._event_queue.put(
            PacketEvent(
                timestamp=datetime.now(),
                source_host=addr[0],
                source_port=addr[1],
                capture_interface=capture_interface,
                address_family=address_family,
                message_kind=message_kind,
                query_types=query_types,
                answer_types=answer_types,
                byte_count=len(payload),
                preview_hex=payload[:16].hex(" "),
                forwarded_count=forwarded,
            )
        )

    def _log(self, level: str, message: str) -> None:
        self._event_queue.put(LogEvent(timestamp=datetime.now(), level=level, message=message))
