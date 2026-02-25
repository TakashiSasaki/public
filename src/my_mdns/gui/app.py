from __future__ import annotations

from datetime import datetime
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
        self._main_service_query_button: ttk.Button | None = None
        self._query_v4_button: ttk.Button | None = None
        self._query_v6_button: ttk.Button | None = None
        self._selected_interface_name: str | None = None
        self._resolve_query_name = tk.StringVar(value="localhost")
        self._resolve_qtype = tk.StringVar(value="A")
        self._resolve_rows_frame: ttk.Frame | None = None
        self._resolve_query_buttons: list[tuple[str, ttk.Button, ttk.Button]] = []
        self._direction_counts: dict[str, int] = {"Query": 0, "Response": 0, "Other": 0}
        self._query_type_counts: dict[str, int] = {}
        self._response_type_counts: dict[str, int] = {}
        self._direction_last_received: dict[str, datetime] = {}
        self._query_type_last_received: dict[str, datetime] = {}
        self._response_type_last_received: dict[str, datetime] = {}
        self._direction_tree: ttk.Treeview | None = None
        self._query_type_tree: ttk.Treeview | None = None
        self._response_type_tree: ttk.Treeview | None = None

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
        stats_tab = ttk.Frame(notebook, padding=8)
        resolve_tab = ttk.Frame(notebook, padding=8)
        logs_tab = ttk.Frame(notebook, padding=8)
        notebook.add(main_tab, text="Main")
        notebook.add(listening_tab, text="Listening")
        notebook.add(stats_tab, text="Stats")
        notebook.add(resolve_tab, text="Resolve")
        notebook.add(logs_tab, text="Logs")

        ctrl = ttk.LabelFrame(main_tab, text="Control", padding=10)
        ctrl.pack(fill=tk.X)

        ttk.Label(ctrl, text="Forward host").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(ctrl, width=18, textvariable=self._target_host).grid(row=0, column=1, padx=6)
        ttk.Label(ctrl, text="Port").grid(row=0, column=2, sticky=tk.W)
        ttk.Entry(ctrl, width=8, textvariable=self._target_port).grid(row=0, column=3, padx=6)
        self._run_toggle_button = tk.Button(ctrl, command=self._toggle_runtime)
        self._run_toggle_button.grid(row=0, column=4, padx=6)
        self._main_service_query_button = ttk.Button(
            ctrl,
            text="Send Services Query",
            command=self._send_main_service_query,
            state=tk.DISABLED,
        )
        self._main_service_query_button.grid(row=0, column=5, padx=6)
        ttk.Button(ctrl, text="Clear target", command=self._clear_target).grid(row=0, column=6, padx=6)
        ttk.Label(ctrl, textvariable=self._status).grid(row=0, column=7, sticky=tk.E, padx=8)
        self._update_run_toggle_ui()

        listening_ctrl = ttk.Frame(listening_tab)
        listening_ctrl.pack(fill=tk.X, pady=(0, 8))
        ttk.Button(listening_ctrl, text="Refresh IFs", command=self._refresh_interfaces).pack(side=tk.LEFT)
        ttk.Button(
            listening_ctrl,
            textvariable=self._ip_filter_button_text,
            command=self._toggle_ip_filter,
        ).pack(side=tk.LEFT, padx=(8, 0))
        self._query_v4_button = ttk.Button(
            listening_ctrl,
            text="Send Query (IPv4)",
            command=self._send_service_query_ipv4,
            state=tk.DISABLED,
        )
        self._query_v4_button.pack(side=tk.LEFT, padx=(16, 0))
        self._query_v6_button = ttk.Button(
            listening_ctrl,
            text="Send Query (IPv6)",
            command=self._send_service_query_ipv6,
            state=tk.DISABLED,
        )
        self._query_v6_button.pack(side=tk.LEFT, padx=(8, 0))

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
        self._iface_status_tree.bind("<<TreeviewSelect>>", self._on_interface_select)
        self._render_interfaces()

        resolve_frame = ttk.LabelFrame(resolve_tab, text="Manual mDNS query", padding=10)
        resolve_frame.pack(fill=tk.BOTH, expand=True)
        ttk.Label(resolve_frame, text="Name").grid(row=0, column=0, sticky=tk.W)
        name_entry = ttk.Entry(resolve_frame, width=28, textvariable=self._resolve_query_name)
        name_entry.grid(row=0, column=1, padx=6, sticky=tk.W)
        name_entry.bind("<KeyRelease>", lambda _e: self._update_manual_query_buttons_state())
        ttk.Label(resolve_frame, text=".local.").grid(row=0, column=2, sticky=tk.W)
        ttk.Label(resolve_frame, text="Type").grid(row=0, column=3, sticky=tk.W)
        qtype_combo = ttk.Combobox(
            resolve_frame,
            width=8,
            textvariable=self._resolve_qtype,
            state="readonly",
            values=("A", "AAAA", "PTR", "SRV", "TXT"),
        )
        qtype_combo.grid(row=0, column=4, padx=6, sticky=tk.W)
        qtype_combo.bind("<<ComboboxSelected>>", lambda _e: self._update_manual_query_buttons_state())

        ttk.Separator(resolve_frame, orient=tk.HORIZONTAL).grid(
            row=1,
            column=0,
            columnspan=5,
            sticky=tk.EW,
            pady=(10, 8),
        )
        ttk.Label(resolve_frame, text="Interface").grid(row=2, column=0, sticky=tk.W)
        ttk.Label(resolve_frame, text="IPv4").grid(row=2, column=1, sticky=tk.W)
        ttk.Label(resolve_frame, text="IPv6").grid(row=2, column=2, sticky=tk.W)
        ttk.Label(resolve_frame, text="Send Query").grid(row=2, column=3, columnspan=2, sticky=tk.W)

        rows_wrap = ttk.Frame(resolve_frame)
        rows_wrap.grid(row=3, column=0, columnspan=5, sticky=tk.NSEW, pady=(6, 0))
        resolve_frame.rowconfigure(3, weight=1)
        resolve_frame.columnconfigure(1, weight=1)
        rows_canvas = tk.Canvas(rows_wrap, highlightthickness=0)
        rows_scroll = ttk.Scrollbar(rows_wrap, orient=tk.VERTICAL, command=rows_canvas.yview)
        rows_canvas.configure(yscrollcommand=rows_scroll.set)
        rows_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        rows_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self._resolve_rows_frame = ttk.Frame(rows_canvas)
        rows_canvas.create_window((0, 0), window=self._resolve_rows_frame, anchor=tk.NW)
        self._resolve_rows_frame.bind(
            "<Configure>",
            lambda _e: rows_canvas.configure(scrollregion=rows_canvas.bbox("all")),
        )
        self._render_resolve_interface_rows()

        stats_summary = ttk.LabelFrame(stats_tab, text="Packet direction counts", padding=8)
        stats_summary.pack(fill=tk.X)
        self._direction_tree = ttk.Treeview(
            stats_summary,
            columns=("kind", "count", "last_received"),
            show="headings",
            height=3,
        )
        self._direction_tree.heading("kind", text="kind")
        self._direction_tree.heading("count", text="count")
        self._direction_tree.heading("last_received", text="last received")
        self._direction_tree.column("kind", width=180, anchor=tk.W)
        self._direction_tree.column("count", width=100, anchor=tk.E)
        self._direction_tree.column("last_received", width=180, anchor=tk.W)
        self._direction_tree.pack(fill=tk.X, expand=True)

        stats_query = ttk.LabelFrame(stats_tab, text="Query QTYPE counts", padding=8)
        stats_query.pack(fill=tk.BOTH, expand=True, pady=(8, 0))
        self._query_type_tree = ttk.Treeview(
            stats_query,
            columns=("qtype", "count", "last_received"),
            show="headings",
            height=8,
        )
        self._query_type_tree.heading("qtype", text="qtype")
        self._query_type_tree.heading("count", text="count")
        self._query_type_tree.heading("last_received", text="last received")
        self._query_type_tree.column("qtype", width=240, anchor=tk.W)
        self._query_type_tree.column("count", width=100, anchor=tk.E)
        self._query_type_tree.column("last_received", width=180, anchor=tk.W)
        self._query_type_tree.pack(fill=tk.BOTH, expand=True)

        stats_response = ttk.LabelFrame(stats_tab, text="Response RR TYPE counts", padding=8)
        stats_response.pack(fill=tk.BOTH, expand=True, pady=(8, 0))
        self._response_type_tree = ttk.Treeview(
            stats_response,
            columns=("rtype", "count", "last_received"),
            show="headings",
            height=8,
        )
        self._response_type_tree.heading("rtype", text="rr type")
        self._response_type_tree.heading("count", text="count")
        self._response_type_tree.heading("last_received", text="last received")
        self._response_type_tree.column("rtype", width=240, anchor=tk.W)
        self._response_type_tree.column("count", width=100, anchor=tk.E)
        self._response_type_tree.column("last_received", width=180, anchor=tk.W)
        self._response_type_tree.pack(fill=tk.BOTH, expand=True)
        self._refresh_stats_views()

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
            self._update_main_service_query_button_state()
            self._update_query_buttons_state()
            self._update_manual_query_buttons_state()

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
            self._update_main_service_query_button_state()
            self._update_query_buttons_state()
            self._update_manual_query_buttons_state()

    def _toggle_runtime(self) -> None:
        if self._running:
            self._stop()
        else:
            self._start()

    def _update_main_service_query_button_state(self) -> None:
        if self._main_service_query_button is None:
            return
        self._main_service_query_button.configure(state=tk.NORMAL if self._running else tk.DISABLED)

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
        self._render_resolve_interface_rows()
        self._update_query_buttons_state()
        self._update_manual_query_buttons_state()
        self._append_log("INFO", f"interfaces refreshed: {len(self._interfaces)} found")

    def _toggle_ip_filter(self) -> None:
        enabled = not self._ip_only_filter.get()
        self._ip_only_filter.set(enabled)
        self._ip_filter_button_text.set(
            "Show IP-assigned only: ON" if enabled else "Show IP-assigned only: OFF"
        )
        self._render_interfaces()
        self._update_query_buttons_state()
        self._update_manual_query_buttons_state()
        self._append_log("INFO", f"ip-assigned filter {'enabled' if enabled else 'disabled'}")

    def _render_interfaces(self) -> None:
        prev_selected = self._selected_interface_name
        for item in self._iface_status_tree.get_children():
            self._iface_status_tree.delete(item)
        restored_item: str | None = None
        for interface in self._interfaces:
            has_ip = bool(interface.ipv4_addresses or interface.ipv6_addresses)
            if self._ip_only_filter.get() and not has_ip:
                continue
            listening = "yes" if self._running else "no"
            ipv4 = ", ".join(interface.ipv4_addresses) if interface.ipv4_addresses else "-"
            ipv6 = ", ".join(interface.ipv6_addresses) if interface.ipv6_addresses else "-"
            item_id = self._iface_status_tree.insert(
                "",
                tk.END,
                values=(interface.name, listening, ipv4, ipv6),
            )
            if prev_selected and interface.name == prev_selected:
                restored_item = item_id
        if restored_item is not None:
            self._iface_status_tree.selection_set(restored_item)
            self._iface_status_tree.focus(restored_item)
            self._selected_interface_name = prev_selected
        else:
            self._selected_interface_name = None
        self._update_query_buttons_state()

    def _on_interface_select(self, _event: tk.Event[tk.Misc]) -> None:
        selection = self._iface_status_tree.selection()
        if not selection:
            self._selected_interface_name = None
            self._update_query_buttons_state()
            return
        values = self._iface_status_tree.item(selection[0], "values")
        if not values:
            self._selected_interface_name = None
        else:
            self._selected_interface_name = str(values[0])
        self._update_query_buttons_state()

    def _get_selected_interface(self) -> InterfaceInfo | None:
        if self._selected_interface_name is None:
            return None
        for interface in self._interfaces:
            if interface.name == self._selected_interface_name:
                return interface
        return None

    def _get_interface_by_name(self, name: str) -> InterfaceInfo | None:
        for interface in self._interfaces:
            if interface.name == name:
                return interface
        return None

    def _render_resolve_interface_rows(self) -> None:
        if self._resolve_rows_frame is None:
            return
        for child in self._resolve_rows_frame.winfo_children():
            child.destroy()

        self._resolve_query_buttons.clear()
        row = 0
        for interface in self._interfaces:
            if not (interface.ipv4_addresses or interface.ipv6_addresses):
                continue
            ipv4_text = ", ".join(interface.ipv4_addresses) if interface.ipv4_addresses else "-"
            ipv6_text = ", ".join(interface.ipv6_addresses) if interface.ipv6_addresses else "-"

            ttk.Label(self._resolve_rows_frame, text=interface.name).grid(row=row, column=0, sticky=tk.W, padx=(0, 6), pady=2)
            ttk.Label(self._resolve_rows_frame, text=ipv4_text).grid(row=row, column=1, sticky=tk.W, padx=(0, 6), pady=2)
            ttk.Label(self._resolve_rows_frame, text=ipv6_text).grid(row=row, column=2, sticky=tk.W, padx=(0, 6), pady=2)

            btn_v4 = ttk.Button(
                self._resolve_rows_frame,
                text="IPv4",
                command=lambda name=interface.name: self._send_manual_query_ipv4(name),
            )
            btn_v4.grid(row=row, column=3, sticky=tk.W, padx=(0, 6), pady=2)
            btn_v6 = ttk.Button(
                self._resolve_rows_frame,
                text="IPv6",
                command=lambda name=interface.name: self._send_manual_query_ipv6(name),
            )
            btn_v6.grid(row=row, column=4, sticky=tk.W, pady=2)
            self._resolve_query_buttons.append((interface.name, btn_v4, btn_v6))
            row += 1

        if row == 0:
            ttk.Label(self._resolve_rows_frame, text="No interface has assigned IP addresses.").grid(
                row=0, column=0, columnspan=5, sticky=tk.W
            )
        self._update_manual_query_buttons_state()

    def _update_query_buttons_state(self) -> None:
        selected = self._get_selected_interface()
        can_use_v4 = bool(self._running and selected and selected.ipv4_addresses)
        can_use_v6 = bool(self._running and selected and selected.ipv6_addresses)
        if self._query_v4_button is not None:
            self._query_v4_button.configure(state=tk.NORMAL if can_use_v4 else tk.DISABLED)
        if self._query_v6_button is not None:
            self._query_v6_button.configure(state=tk.NORMAL if can_use_v6 else tk.DISABLED)

    def _send_service_query_ipv4(self) -> None:
        selected = self._get_selected_interface()
        if not self._running or selected is None or not selected.ipv4_addresses:
            self._update_query_buttons_state()
            return
        try:
            self._runtime.send_service_query_ipv4(selected.ipv4_addresses[0])
        except OSError:
            self._append_log("ERROR", f"service query IPv4 failed on {selected.name}")

    def _send_service_query_ipv6(self) -> None:
        selected = self._get_selected_interface()
        if not self._running or selected is None or not selected.ipv6_addresses:
            self._update_query_buttons_state()
            return
        try:
            self._runtime.send_service_query_ipv6(selected.name)
        except OSError:
            self._append_log("ERROR", f"service query IPv6 failed on {selected.name}")

    def _send_main_service_query(self) -> None:
        if not self._running:
            self._update_main_service_query_button_state()
            return
        sent_v4 = 0
        sent_v6 = 0
        for interface in self._interfaces:
            if interface.ipv4_addresses:
                try:
                    self._runtime.send_service_query_ipv4(interface.ipv4_addresses[0])
                    sent_v4 += 1
                except OSError:
                    self._append_log("ERROR", f"service query IPv4 failed on {interface.name}")
            if interface.ipv6_addresses:
                try:
                    self._runtime.send_service_query_ipv6(interface.name)
                    sent_v6 += 1
                except OSError:
                    self._append_log("ERROR", f"service query IPv6 failed on {interface.name}")
        self._append_log("INFO", f"sent service query on interfaces: ipv4={sent_v4}, ipv6={sent_v6}")

    def _update_manual_query_buttons_state(self) -> None:
        has_name = bool(self._resolve_query_name.get().strip())
        for interface_name, btn_v4, btn_v6 in self._resolve_query_buttons:
            selected = self._get_interface_by_name(interface_name)
            can_use_v4 = bool(self._running and has_name and selected and selected.ipv4_addresses)
            can_use_v6 = bool(self._running and has_name and selected and selected.ipv6_addresses)
            btn_v4.configure(state=tk.NORMAL if can_use_v4 else tk.DISABLED)
            btn_v6.configure(state=tk.NORMAL if can_use_v6 else tk.DISABLED)

    def _build_resolve_fqdn(self) -> str | None:
        base = self._resolve_query_name.get().strip().rstrip(".")
        if not base:
            return None
        if base.endswith(".local"):
            return base + "."
        return base + ".local."

    def _send_manual_query_ipv4(self, interface_name: str) -> None:
        qname = self._build_resolve_fqdn()
        qtype = self._resolve_qtype.get().strip().upper()
        selected = self._get_interface_by_name(interface_name)
        if not self._running or qname is None or selected is None or not selected.ipv4_addresses:
            self._update_manual_query_buttons_state()
            return
        try:
            self._runtime.send_manual_query_ipv4(selected.ipv4_addresses[0], qname, qtype)
        except (OSError, ValueError):
            self._append_log("ERROR", f"manual query IPv4 failed on {selected.name}")

    def _send_manual_query_ipv6(self, interface_name: str) -> None:
        qname = self._build_resolve_fqdn()
        qtype = self._resolve_qtype.get().strip().upper()
        selected = self._get_interface_by_name(interface_name)
        if not self._running or qname is None or selected is None or not selected.ipv6_addresses:
            self._update_manual_query_buttons_state()
            return
        try:
            self._runtime.send_manual_query_ipv6(selected.name, qname, qtype)
        except (OSError, ValueError):
            self._append_log("ERROR", f"manual query IPv6 failed on {selected.name}")

    def _poll_events(self) -> None:
        while True:
            try:
                event = self._events.get_nowait()
            except Empty:
                break
            if isinstance(event, PacketEvent):
                self._accumulate_stats(event)
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

    def _accumulate_stats(self, event: PacketEvent) -> None:
        self._direction_counts[event.message_kind] = self._direction_counts.get(event.message_kind, 0) + 1
        self._direction_last_received[event.message_kind] = event.timestamp
        for qtype in event.query_types:
            self._query_type_counts[qtype] = self._query_type_counts.get(qtype, 0) + 1
            self._query_type_last_received[qtype] = event.timestamp
        for rtype in event.answer_types:
            self._response_type_counts[rtype] = self._response_type_counts.get(rtype, 0) + 1
            self._response_type_last_received[rtype] = event.timestamp
        self._refresh_stats_views()

    def _refresh_stats_views(self) -> None:
        def _format_last_received(ts: datetime | None) -> str:
            if ts is None:
                return "-"
            return ts.strftime("%H:%M:%S.%f")[:-3]

        if self._direction_tree is not None:
            for item in self._direction_tree.get_children():
                self._direction_tree.delete(item)
            for kind in ("Query", "Response", "Other"):
                self._direction_tree.insert(
                    "",
                    tk.END,
                    values=(
                        kind,
                        self._direction_counts.get(kind, 0),
                        _format_last_received(self._direction_last_received.get(kind)),
                    ),
                )

        if self._query_type_tree is not None:
            for item in self._query_type_tree.get_children():
                self._query_type_tree.delete(item)
            for qtype, count in sorted(self._query_type_counts.items(), key=lambda kv: (-kv[1], kv[0])):
                self._query_type_tree.insert(
                    "",
                    tk.END,
                    values=(qtype, count, _format_last_received(self._query_type_last_received.get(qtype))),
                )

        if self._response_type_tree is not None:
            for item in self._response_type_tree.get_children():
                self._response_type_tree.delete(item)
            for rtype, count in sorted(self._response_type_counts.items(), key=lambda kv: (-kv[1], kv[0])):
                self._response_type_tree.insert(
                    "",
                    tk.END,
                    values=(rtype, count, _format_last_received(self._response_type_last_received.get(rtype))),
                )

    def _append_log(self, level: str, message: str, time_text: str | None = None) -> None:
        if not self._log_text.winfo_exists():
            return
        prefix = f"[{time_text}] " if time_text else ""
        self._log_text.configure(state=tk.NORMAL)
        self._log_text.insert(tk.END, f"{prefix}{level} {message}\n")
        self._log_text.see(tk.END)
        self._log_text.configure(state=tk.DISABLED)

    def shutdown(self) -> None:
        try:
            self._runtime.stop()
        except Exception as exc:
            self._append_log("ERROR", f"failed to stop runtime during shutdown: {exc}")
        self._running = False
        self._status.set("stopped")
        self._render_interfaces()
        self._update_run_toggle_ui()
        self._update_main_service_query_button_state()
        self._update_query_buttons_state()
        self._update_manual_query_buttons_state()
        if self.root.winfo_exists():
            self.root.quit()
            self.root.destroy()

    def _on_close(self) -> None:
        self.shutdown()

    def run(self) -> None:
        self.root.mainloop()
