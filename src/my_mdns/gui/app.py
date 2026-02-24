from __future__ import annotations

from queue import Empty, Queue
import tkinter as tk
from tkinter import ttk

from my_mdns.core.events import LogEvent, PacketEvent
from my_mdns.core.interfaces import list_interfaces
from my_mdns.core.runtime import CoreRuntime


class MDNSApp:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("my-mdns prototype")
        self.root.geometry("920x520")

        self._events: Queue[PacketEvent | LogEvent] = Queue()
        self._runtime = CoreRuntime(self._events)
        self._running = False

        self._target_host = tk.StringVar(value="127.0.0.1")
        self._target_port = tk.StringVar(value="5353")
        self._status = tk.StringVar(value="stopped")
        self._interfaces = list_interfaces()

        self._build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.after(150, self._poll_events)

    def _build_ui(self) -> None:
        frame = ttk.Frame(self.root, padding=12)
        frame.pack(fill=tk.BOTH, expand=True)

        ctrl = ttk.LabelFrame(frame, text="Control", padding=10)
        ctrl.pack(fill=tk.X)

        ttk.Label(ctrl, text="Forward host").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(ctrl, width=18, textvariable=self._target_host).grid(row=0, column=1, padx=6)
        ttk.Label(ctrl, text="Port").grid(row=0, column=2, sticky=tk.W)
        ttk.Entry(ctrl, width=8, textvariable=self._target_port).grid(row=0, column=3, padx=6)
        ttk.Button(ctrl, text="Start", command=self._start).grid(row=0, column=4, padx=6)
        ttk.Button(ctrl, text="Stop", command=self._stop).grid(row=0, column=5, padx=6)
        ttk.Button(ctrl, text="Clear target", command=self._clear_target).grid(row=0, column=6, padx=6)
        ttk.Button(ctrl, text="Refresh IFs", command=self._refresh_interfaces).grid(row=0, column=7, padx=6)
        ttk.Label(ctrl, textvariable=self._status).grid(row=0, column=8, sticky=tk.E, padx=8)

        iface = ttk.LabelFrame(frame, text="Listen interfaces", padding=8)
        iface.pack(fill=tk.BOTH, expand=False, pady=(10, 0))
        iface_notebook = ttk.Notebook(iface)
        iface_notebook.pack(fill=tk.BOTH, expand=True)

        iface_list_tab = ttk.Frame(iface_notebook)
        iface_status_tab = ttk.Frame(iface_notebook)
        iface_notebook.add(iface_list_tab, text="Interfaces")
        iface_notebook.add(iface_status_tab, text="Listening")

        self._iface_list_tree = ttk.Treeview(
            iface_list_tab,
            columns=("name",),
            show="headings",
            height=5,
        )
        self._iface_list_tree.heading("name", text="interface")
        self._iface_list_tree.column("name", width=520, anchor=tk.W)
        self._iface_list_tree.pack(fill=tk.BOTH, expand=True)

        self._iface_status_tree = ttk.Treeview(
            iface_status_tab,
            columns=("name", "listening"),
            show="headings",
            height=5,
        )
        self._iface_status_tree.heading("name", text="interface")
        self._iface_status_tree.heading("listening", text="listening")
        self._iface_status_tree.column("name", width=420, anchor=tk.W)
        self._iface_status_tree.column("listening", width=120, anchor=tk.W)
        self._iface_status_tree.pack(fill=tk.BOTH, expand=True)
        self._render_interfaces()

        table = ttk.LabelFrame(frame, text="Captured packets", padding=8)
        table.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        self._tree = ttk.Treeview(
            table,
            columns=("time", "source", "size", "forwarded", "preview"),
            show="headings",
            height=12,
        )
        for name, title, width in (
            ("time", "time", 130),
            ("source", "source", 160),
            ("size", "bytes", 70),
            ("forwarded", "fwd", 60),
            ("preview", "preview", 430),
        ):
            self._tree.heading(name, text=title)
            self._tree.column(name, width=width, anchor=tk.W)
        self._tree.pack(fill=tk.BOTH, expand=True)

        logs = ttk.LabelFrame(frame, text="Logs", padding=8)
        logs.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        self._log_text = tk.Text(logs, height=7, state=tk.DISABLED)
        self._log_text.pack(fill=tk.BOTH, expand=True)

    def _start(self) -> None:
        if self._running:
            return
        self._runtime.start()
        self._running = True
        self._status.set("running")
        self._render_interfaces()
        self._apply_target()

    def _stop(self) -> None:
        if not self._running:
            return
        self._runtime.stop()
        self._running = False
        self._status.set("stopped")
        self._render_interfaces()

    def _apply_target(self) -> None:
        host = self._target_host.get().strip()
        port_text = self._target_port.get().strip()
        if not host:
            self._runtime.clear_forward_target()
            return
        try:
            port = int(port_text)
        except ValueError:
            self._append_log("ERROR", f"invalid port: {port_text}")
            return
        self._runtime.set_forward_target(host, port)

    def _clear_target(self) -> None:
        self._runtime.clear_forward_target()
        self._append_log("INFO", "forward target cleared")

    def _refresh_interfaces(self) -> None:
        self._interfaces = list_interfaces()
        self._render_interfaces()
        self._append_log("INFO", f"interfaces refreshed: {len(self._interfaces)} found")

    def _render_interfaces(self) -> None:
        for item in self._iface_list_tree.get_children():
            self._iface_list_tree.delete(item)
        for item in self._iface_status_tree.get_children():
            self._iface_status_tree.delete(item)
        for name in self._interfaces:
            listening = "yes" if self._running else "no"
            self._iface_list_tree.insert("", tk.END, values=(name,))
            self._iface_status_tree.insert("", tk.END, values=(name, listening))

    def _poll_events(self) -> None:
        while True:
            try:
                event = self._events.get_nowait()
            except Empty:
                break
            if isinstance(event, PacketEvent):
                self._tree.insert(
                    "",
                    0,
                    values=(
                        event.timestamp.strftime("%H:%M:%S.%f")[:-3],
                        f"{event.source_host}:{event.source_port}",
                        event.byte_count,
                        event.forwarded_count,
                        event.preview_hex,
                    ),
                )
                for item in self._tree.get_children()[300:]:
                    self._tree.delete(item)
            else:
                self._append_log(event.level, event.message, event.timestamp.strftime("%H:%M:%S"))
        self.root.after(150, self._poll_events)

    def _append_log(self, level: str, message: str, time_text: str | None = None) -> None:
        prefix = f"[{time_text}] " if time_text else ""
        self._log_text.configure(state=tk.NORMAL)
        self._log_text.insert(tk.END, f"{prefix}{level} {message}\n")
        self._log_text.see(tk.END)
        self._log_text.configure(state=tk.DISABLED)

    def _on_close(self) -> None:
        self._stop()
        self.root.destroy()

    def run(self) -> None:
        self.root.mainloop()
