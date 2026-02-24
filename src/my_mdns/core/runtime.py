from __future__ import annotations

import asyncio
import threading
from datetime import datetime
from queue import Queue

from my_mdns.core.capture import MDNSCapture
from my_mdns.core.events import LogEvent, PacketEvent
from my_mdns.core.forwarder import MDNSForwarder


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

    def _run_loop(self) -> None:
        if self._loop is None:
            return
        asyncio.set_event_loop(self._loop)
        self._loop_ready.set()
        self._loop.run_forever()

    def _on_packet(self, payload: bytes, addr: tuple[str, int]) -> None:
        forwarded = 0
        try:
            if self._forwarder is not None:
                forwarded = self._forwarder.forward(payload)
        except OSError as exc:
            self._log("ERROR", f"forward error: {exc}")

        self._event_queue.put(
            PacketEvent(
                timestamp=datetime.now(),
                source_host=addr[0],
                source_port=addr[1],
                byte_count=len(payload),
                preview_hex=payload[:16].hex(" "),
                forwarded_count=forwarded,
            )
        )

    def _log(self, level: str, message: str) -> None:
        self._event_queue.put(LogEvent(timestamp=datetime.now(), level=level, message=message))
