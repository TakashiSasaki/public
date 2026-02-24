from __future__ import annotations

from queue import Empty, Queue
import tkinter as tk
from tkinter import ttk

from my_mdns.core.events import LogEvent, PacketEvent
from my_mdns.core.interfaces import InterfaceInfo, list_interfaces
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
        self._interfaces: list[InterfaceInfo] = list_interfaces()
        self._ip_only_filter = tk.BooleanVar(value=True)
        self._ip_filter_button_text = tk.StringVar(value="Show IP-assigned only: ON")
        self._run_toggle_button: tk.Button | None = None

        self._build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.after(150, self._poll_events)
        self.root.after(0, self._start)

    def _build_ui(self) -> None:
        frame = ttk.Frame(self.root, padding=12)
        frame.pack(fill=tk.BOTH, expand=True)

        notebook = ttk.Notebook(frame)
        notebook.pack(fill=tk.BOTH, expand=True)

        main_tab = ttk.Frame(notebook, padding=8)
        listening_tab = ttk.Frame(notebook, padding=8)
        logs_tab = ttk.Frame(notebook, padding=8)
        notebook.add(main_tab, text="Main")
        notebook.add(listening_tab, text="Listening")
        notebook.add(logs_tab, text="Logs")

        ctrl = ttk.LabelFrame(main_tab, text="Control", padding=10)
        ctrl.pack(fill=tk.X)

        ttk.Label(ctrl, text="Forward host").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(ctrl, width=18, textvariable=self._target_host).grid(row=0, column=1, padx=6)
        ttk.Label(ctrl, text="Port").grid(row=0, column=2, sticky=tk.W)
        ttk.Entry(ctrl, width=8, textvariable=self._target_port).grid(row=0, column=3, padx=6)
        self._run_toggle_button = tk.Button(ctrl, command=self._toggle_runtime)
        self._run_toggle_button.grid(row=0, column=4, padx=6)
        ttk.Button(ctrl, text="Clear target", command=self._clear_target).grid(row=0, column=5, padx=6)
        ttk.Label(ctrl, textvariable=self._status).grid(row=0, column=6, sticky=tk.E, padx=8)
        self._update_run_toggle_ui()

        listening_ctrl = ttk.Frame(listening_tab)
        listening_ctrl.pack(fill=tk.X, pady=(0, 8))
        ttk.Button(listening_ctrl, text="Refresh IFs", command=self._refresh_interfaces).pack(side=tk.LEFT)
        ttk.Button(
            listening_ctrl,
            textvariable=self._ip_filter_button_text,
            command=self._toggle_ip_filter,
        ).pack(side=tk.LEFT, padx=(8, 0))

        iface = ttk.LabelFrame(listening_tab, text="Listen interfaces", padding=8)
        iface.pack(fill=tk.BOTH, expand=True)
        self._iface_status_tree = ttk.Treeview(
            iface,
            columns=("name", "listening", "ipv4", "ipv6"),
            show="headings",
            height=16,
        )
        self._iface_status_tree.heading("name", text="interface")
        self._iface_status_tree.heading("listening", text="listening")
        self._iface_status_tree.heading("ipv4", text="ipv4 addresses")
        self._iface_status_tree.heading("ipv6", text="ipv6 addresses")
        self._iface_status_tree.column("name", width=240, anchor=tk.W)
        self._iface_status_tree.column("listening", width=100, anchor=tk.W)
        self._iface_status_tree.column("ipv4", width=220, anchor=tk.W)
        self._iface_status_tree.column("ipv6", width=300, anchor=tk.W)
        self._iface_status_tree.pack(fill=tk.BOTH, expand=True)
        self._render_interfaces()

        table = ttk.LabelFrame(main_tab, text="Captured packets", padding=8)
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

        logs = ttk.LabelFrame(logs_tab, text="Logs", padding=8)
        logs.pack(fill=tk.BOTH, expand=True)
        self._log_text = tk.Text(logs, height=7, state=tk.DISABLED)
        self._log_text.pack(fill=tk.BOTH, expand=True)

    def _start(self) -> None:
        if self._running:
            return
        try:
            self._runtime.start()
            self._running = True
            self._status.set("running")
            self._apply_target()
        except Exception as exc:
            self._running = False
            self._status.set("stopped")
            self._append_log("ERROR", f"failed to start capture: {exc}")
        finally:
            self._render_interfaces()
            self._update_run_toggle_ui()

    def _stop(self) -> None:
        if not self._running:
            return
        try:
            self._runtime.stop()
            self._running = False
            self._status.set("stopped")
        except Exception as exc:
            self._append_log("ERROR", f"failed to stop capture: {exc}")
        finally:
            self._render_interfaces()
            self._update_run_toggle_ui()

    def _toggle_runtime(self) -> None:
        if self._running:
            self._stop()
        else:
            self._start()

    def _update_run_toggle_ui(self) -> None:
        if self._run_toggle_button is None:
            return
        if self._running:
            self._run_toggle_button.configure(
                text="Stop Listening",
                bg="#16a34a",
                fg="#ffffff",
                activebackground="#15803d",
                activeforeground="#ffffff",
            )
        else:
            self._run_toggle_button.configure(
                text="Start Listening",
                bg="#9ca3af",
                fg="#111827",
                activebackground="#6b7280",
                activeforeground="#111827",
            )

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

    def _toggle_ip_filter(self) -> None:
        enabled = not self._ip_only_filter.get()
        self._ip_only_filter.set(enabled)
        self._ip_filter_button_text.set(
            "Show IP-assigned only: ON" if enabled else "Show IP-assigned only: OFF"
        )
        self._render_interfaces()
        self._append_log("INFO", f"ip-assigned filter {'enabled' if enabled else 'disabled'}")

    def _render_interfaces(self) -> None:
        for item in self._iface_status_tree.get_children():
            self._iface_status_tree.delete(item)
        for interface in self._interfaces:
            has_ip = bool(interface.ipv4_addresses or interface.ipv6_addresses)
            if self._ip_only_filter.get() and not has_ip:
                continue
            listening = "yes" if self._running else "no"
            ipv4 = ", ".join(interface.ipv4_addresses) if interface.ipv4_addresses else "-"
            ipv6 = ", ".join(interface.ipv6_addresses) if interface.ipv6_addresses else "-"
            self._iface_status_tree.insert(
                "",
                tk.END,
                values=(interface.name, listening, ipv4, ipv6),
            )

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
