from __future__ import annotations

from datetime import datetime
from queue import Empty, Queue
import tkinter as tk
from tkinter import ttk

from my_mdns.core.events import (
    LogEvent,
    PacketEvent,
    ARecordEvent,
    AAAARecordEvent,
    SRVRecordEvent,
    PTRRecordEvent,
    TXTRecordEvent,
    QueryEvent,
)
from my_mdns.core.interfaces import InterfaceInfo, list_interfaces
from my_mdns.core.runtime import CoreRuntime


class MDNSApp:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("mdns-inspector prototype")
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
        self._interface_packet_counts: dict[str, dict[str, int]] = {}
        self._direction_counts: dict[str, int] = {"Query": 0, "Response": 0, "Other": 0}
        self._query_type_counts: dict[str, int] = {}
        self._response_type_counts: dict[str, int] = {}
        self._direction_last_received: dict[str, datetime] = {}
        self._query_type_last_received: dict[str, datetime] = {}
        self._response_type_last_received: dict[str, datetime] = {}
        self._direction_tree: ttk.Treeview | None = None
        self._query_type_tree: ttk.Treeview | None = None
        self._response_type_tree: ttk.Treeview | None = None
        self._a_records_tree: ttk.Treeview | None = None
        self._aaaa_records_tree: ttk.Treeview | None = None
        self._srv_records_tree: ttk.Treeview | None = None
        self._ptr_records_tree: ttk.Treeview | None = None
        self._txt_records_tree: ttk.Treeview | None = None
        self._queries_tree: ttk.Treeview | None = None

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
        a_records_tab = ttk.Frame(notebook, padding=8)
        aaaa_records_tab = ttk.Frame(notebook, padding=8)
        srv_records_tab = ttk.Frame(notebook, padding=8)
        ptr_records_tab = ttk.Frame(notebook, padding=8)
        txt_records_tab = ttk.Frame(notebook, padding=8)
        queries_tab = ttk.Frame(notebook, padding=8)
        logs_tab = ttk.Frame(notebook, padding=8)
        notebook.add(main_tab, text="Main")
        notebook.add(listening_tab, text="Listening")
        notebook.add(stats_tab, text="Stats")
        notebook.add(resolve_tab, text="Resolve")
        notebook.add(a_records_tab, text="A Records")
        notebook.add(aaaa_records_tab, text="AAAA Records")
        notebook.add(srv_records_tab, text="SRV Records")
        notebook.add(ptr_records_tab, text="PTR Records")
        notebook.add(txt_records_tab, text="TXT Records")
        notebook.add(queries_tab, text="Queries")
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
            columns=("name", "listening", "ipv4", "ipv6", "rx4", "tx4", "rx6", "tx6"),
            show="headings",
            height=16,
        )
        self._iface_status_tree.heading("name", text="interface")
        self._iface_status_tree.heading("listening", text="listening")
        self._iface_status_tree.heading("ipv4", text="ipv4 addresses")
        self._iface_status_tree.heading("ipv6", text="ipv6 addresses")
        self._iface_status_tree.heading("rx4", text="rx4")
        self._iface_status_tree.heading("tx4", text="tx4")
        self._iface_status_tree.heading("rx6", text="rx6")
        self._iface_status_tree.heading("tx6", text="tx6")
        self._iface_status_tree.column("name", width=120, minwidth=30, anchor=tk.W)
        self._iface_status_tree.column("listening", width=30, minwidth=30, anchor=tk.W)
        self._iface_status_tree.column("ipv4", width=100, minwidth=30, anchor=tk.W)
        self._iface_status_tree.column("ipv6", width=220, minwidth=30, anchor=tk.W)
        self._iface_status_tree.column("rx4", width=40, minwidth=30, anchor=tk.E)
        self._iface_status_tree.column("tx4", width=40, minwidth=30, anchor=tk.E)
        self._iface_status_tree.column("rx6", width=40, minwidth=30, anchor=tk.E)
        self._iface_status_tree.column("tx6", width=20, minwidth=20, anchor=tk.E)
        self._iface_status_tree.pack(fill=tk.BOTH, expand=True)
        self._load_column_widths("interfaces", self._iface_status_tree)
        self._iface_status_tree.bind("<ButtonRelease-1>", lambda e: self._on_tree_release(e, "interfaces"))
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
        self._direction_tree.column("kind", width=180, minwidth=30, anchor=tk.W)
        self._direction_tree.column("count", width=100, minwidth=30, anchor=tk.E)
        self._direction_tree.column("last_received", width=180, minwidth=30, anchor=tk.W)
        self._direction_tree.pack(fill=tk.X, expand=True)
        self._load_column_widths("stats_direction", self._direction_tree)
        self._direction_tree.bind("<ButtonRelease-1>", lambda e: self._on_tree_release(e, "stats_direction"))

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
        self._query_type_tree.column("qtype", width=240, minwidth=30, anchor=tk.W)
        self._query_type_tree.column("count", width=100, minwidth=30, anchor=tk.E)
        self._query_type_tree.column("last_received", width=180, minwidth=30, anchor=tk.W)
        self._query_type_tree.pack(fill=tk.BOTH, expand=True)
        self._load_column_widths("stats_query", self._query_type_tree)
        self._query_type_tree.bind("<ButtonRelease-1>", lambda e: self._on_tree_release(e, "stats_query"))

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
        self._response_type_tree.column("rtype", width=240, minwidth=30, anchor=tk.W)
        self._response_type_tree.column("count", width=100, minwidth=30, anchor=tk.E)
        self._response_type_tree.column("last_received", width=180, minwidth=30, anchor=tk.W)
        self._response_type_tree.pack(fill=tk.BOTH, expand=True)
        self._load_column_widths("stats_response", self._response_type_tree)
        self._response_type_tree.bind("<ButtonRelease-1>", lambda e: self._on_tree_release(e, "stats_response"))
        self._refresh_stats_views()

        table = ttk.LabelFrame(main_tab, text="Captured packets", padding=8)
        table.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        self._tree = ttk.Treeview(
            table,
            columns=("time", "source", "type", "rr_types", "size", "forwarded", "preview"),
            show="headings",
            height=12,
        )
        for name, title, width in (
            ("time", "time", 100),
            ("source", "source", 160),
            ("type", "type", 80),
            ("rr_types", "rr_types", 120),
            ("size", "bytes", 60),
            ("forwarded", "fwd", 50),
            ("preview", "preview", 260),
        ):
            self._tree.heading(name, text=title)
            self._tree.column(name, width=width, minwidth=30, anchor=tk.W)
        self._tree.pack(fill=tk.BOTH, expand=True)
        self._load_column_widths("main", self._tree)
        self._tree.bind("<ButtonRelease-1>", lambda e: self._on_tree_release(e, "main"))

        a_records_frame = ttk.LabelFrame(a_records_tab, text="A Records (Name -> IP)", padding=8)
        a_records_frame.pack(fill=tk.BOTH, expand=True)
        self._a_records_tree = ttk.Treeview(
            a_records_frame,
            columns=("name", "ip", "destination", "last_seen", "source_ip"),
            show="headings",
        )
        self._a_records_tree.heading("name", text="Name")
        self._a_records_tree.heading("ip", text="IP Address")
        self._a_records_tree.heading("destination", text="Destination")
        self._a_records_tree.heading("last_seen", text="Last Seen")
        self._a_records_tree.heading("source_ip", text="Source IP")
        self._a_records_tree.column("name", width=250, minwidth=30, anchor=tk.W)
        self._a_records_tree.column("ip", width=150, minwidth=30, anchor=tk.W)
        self._a_records_tree.column("destination", width=100, minwidth=30, anchor=tk.W)
        self._a_records_tree.column("last_seen", width=180, minwidth=30, anchor=tk.W)
        self._a_records_tree.column("source_ip", width=120, minwidth=30, anchor=tk.W)
        self._a_records_tree.pack(fill=tk.BOTH, expand=True)
        self._load_column_widths("records_a", self._a_records_tree)
        self._a_records_tree.bind("<ButtonRelease-1>", lambda e: self._on_tree_release(e, "records_a"))

        aaaa_records_frame = ttk.LabelFrame(aaaa_records_tab, text="AAAA Records (Name -> IPv6)", padding=8)
        aaaa_records_frame.pack(fill=tk.BOTH, expand=True)
        self._aaaa_records_tree = ttk.Treeview(aaaa_records_frame, columns=("name", "ip", "destination", "last_seen", "source_ip"), show="headings")
        self._aaaa_records_tree.heading("name", text="Name")
        self._aaaa_records_tree.heading("ip", text="IPv6 Address")
        self._aaaa_records_tree.heading("destination", text="Destination")
        self._aaaa_records_tree.heading("last_seen", text="Last Seen")
        self._aaaa_records_tree.heading("source_ip", text="Source IP")
        self._aaaa_records_tree.column("name", width=250, minwidth=30, anchor=tk.W)
        self._aaaa_records_tree.column("ip", width=250, minwidth=30, anchor=tk.W)
        self._aaaa_records_tree.column("destination", width=100, minwidth=30, anchor=tk.W)
        self._aaaa_records_tree.column("last_seen", width=180, minwidth=30, anchor=tk.W)
        self._aaaa_records_tree.column("source_ip", width=120, minwidth=30, anchor=tk.W)
        self._aaaa_records_tree.pack(fill=tk.BOTH, expand=True)
        self._load_column_widths("records_aaaa", self._aaaa_records_tree)
        self._aaaa_records_tree.bind("<ButtonRelease-1>", lambda e: self._on_tree_release(e, "records_aaaa"))

        srv_records_frame = ttk.LabelFrame(srv_records_tab, text="SRV Records", padding=8)
        srv_records_frame.pack(fill=tk.BOTH, expand=True)
        self._srv_records_tree = ttk.Treeview(srv_records_frame, columns=("name", "target", "port", "priority", "weight", "last_seen", "source_ip"), show="headings")
        self._srv_records_tree.heading("name", text="Name")
        self._srv_records_tree.heading("target", text="Target")
        self._srv_records_tree.heading("port", text="Port")
        self._srv_records_tree.heading("priority", text="Priority")
        self._srv_records_tree.heading("weight", text="Weight")
        self._srv_records_tree.heading("last_seen", text="Last Seen")
        self._srv_records_tree.heading("source_ip", text="Source IP")
        self._srv_records_tree.column("name", width=200, minwidth=30, anchor=tk.W)
        self._srv_records_tree.column("target", width=200, minwidth=30, anchor=tk.W)
        self._srv_records_tree.column("port", width=60, minwidth=30, anchor=tk.E)
        self._srv_records_tree.column("priority", width=60, minwidth=30, anchor=tk.E)
        self._srv_records_tree.column("weight", width=60, minwidth=30, anchor=tk.E)
        self._srv_records_tree.column("last_seen", width=180, minwidth=30, anchor=tk.W)
        self._srv_records_tree.column("source_ip", width=120, minwidth=30, anchor=tk.W)
        self._srv_records_tree.pack(fill=tk.BOTH, expand=True)
        self._load_column_widths("records_srv", self._srv_records_tree)
        self._srv_records_tree.bind("<ButtonRelease-1>", lambda e: self._on_tree_release(e, "records_srv"))

        ptr_records_frame = ttk.LabelFrame(ptr_records_tab, text="PTR Records", padding=8)
        ptr_records_frame.pack(fill=tk.BOTH, expand=True)
        self._ptr_records_tree = ttk.Treeview(ptr_records_frame, columns=("name", "ptrdname", "last_seen", "source_ip"), show="headings")
        self._ptr_records_tree.heading("name", text="Name")
        self._ptr_records_tree.heading("ptrdname", text="Target Domain Name (PTRDNAME)")
        self._ptr_records_tree.heading("last_seen", text="Last Seen")
        self._ptr_records_tree.heading("source_ip", text="Source IP")
        self._ptr_records_tree.column("name", width=200, minwidth=30, anchor=tk.W)
        self._ptr_records_tree.column("ptrdname", width=300, minwidth=30, anchor=tk.W)
        self._ptr_records_tree.column("last_seen", width=180, minwidth=30, anchor=tk.W)
        self._ptr_records_tree.column("source_ip", width=120, minwidth=30, anchor=tk.W)
        self._ptr_records_tree.pack(fill=tk.BOTH, expand=True)
        self._load_column_widths("records_ptr", self._ptr_records_tree)
        self._ptr_records_tree.bind("<ButtonRelease-1>", lambda e: self._on_tree_release(e, "records_ptr"))

        txt_records_frame = ttk.LabelFrame(txt_records_tab, text="TXT Records", padding=8)
        txt_records_frame.pack(fill=tk.BOTH, expand=True)
        self._txt_records_tree = ttk.Treeview(txt_records_frame, columns=("name", "text", "last_seen", "source_ip"), show="headings")
        self._txt_records_tree.heading("name", text="Name")
        self._txt_records_tree.heading("text", text="Text Content")
        self._txt_records_tree.heading("last_seen", text="Last Seen")
        self._txt_records_tree.heading("source_ip", text="Source IP")
        self._txt_records_tree.column("name", width=200, minwidth=30, anchor=tk.W)
        self._txt_records_tree.column("text", width=300, minwidth=30, anchor=tk.W)
        self._txt_records_tree.column("last_seen", width=180, minwidth=30, anchor=tk.W)
        self._txt_records_tree.column("source_ip", width=120, minwidth=30, anchor=tk.W)
        self._txt_records_tree.pack(fill=tk.BOTH, expand=True)
        self._load_column_widths("records_txt", self._txt_records_tree)
        self._txt_records_tree.bind("<ButtonRelease-1>", lambda e: self._on_tree_release(e, "records_txt"))

        queries_frame = ttk.LabelFrame(queries_tab, text="mDNS Queries (Requests)", padding=8)
        queries_frame.pack(fill=tk.BOTH, expand=True)
        self._queries_tree = ttk.Treeview(queries_frame, columns=("name", "type", "count", "last_seen", "source_ip"), show="headings")
        self._queries_tree.heading("name", text="Name")
        self._queries_tree.heading("type", text="Type")
        self._queries_tree.heading("count", text="Count")
        self._queries_tree.heading("last_seen", text="Last Seen")
        self._queries_tree.heading("source_ip", text="Last Client IP")
        self._queries_tree.column("name", width=250, minwidth=30, anchor=tk.W)
        self._queries_tree.column("type", width=80, minwidth=30, anchor=tk.W)
        self._queries_tree.column("count", width=80, minwidth=30, anchor=tk.E)
        self._queries_tree.column("last_seen", width=180, minwidth=30, anchor=tk.W)
        self._queries_tree.column("source_ip", width=120, minwidth=30, anchor=tk.W)
        self._queries_tree.pack(fill=tk.BOTH, expand=True)
        self._load_column_widths("queries", self._queries_tree)
        self._queries_tree.bind("<ButtonRelease-1>", lambda e: self._on_tree_release(e, "queries"))

        self._load_all_records_from_db()

        logs = ttk.LabelFrame(logs_tab, text="Logs", padding=8)
        logs.pack(fill=tk.BOTH, expand=True)
        self._log_text = tk.Text(logs, height=7, state=tk.DISABLED)
        self._log_text.pack(fill=tk.BOTH, expand=True)

    def _load_all_records_from_db(self) -> None:
        from my_mdns.core import store
        
        # Load A Records
        if self._a_records_tree is not None:
            for item in self._a_records_tree.get_children():
                self._a_records_tree.delete(item)
            try:
                for name, ip, last_seen, source_ip, is_multicast in store.get_all_a_records():
                    dest = "Multicast" if is_multicast else "Unicast"
                    self._a_records_tree.insert("", tk.END, values=(name, ip, dest, last_seen, source_ip))
            except Exception as e:
                self._append_log("ERROR", f"Failed to load A records: {e}")

        # Load AAAA Records
        if self._aaaa_records_tree is not None:
            for item in self._aaaa_records_tree.get_children():
                self._aaaa_records_tree.delete(item)
            try:
                for name, ip, last_seen, source_ip, is_multicast in store.get_all_aaaa_records():
                    dest = "Multicast" if is_multicast else "Unicast"
                    self._aaaa_records_tree.insert("", tk.END, values=(name, ip, dest, last_seen, source_ip))
            except Exception as e:
                self._append_log("ERROR", f"Failed to load AAAA records: {e}")

        # Load SRV Records
        if self._srv_records_tree is not None:
            for item in self._srv_records_tree.get_children():
                self._srv_records_tree.delete(item)
            try:
                for name, target, port, priority, weight, last_seen, source_ip in store.get_all_srv_records():
                    self._srv_records_tree.insert("", tk.END, values=(name, target, port, priority, weight, last_seen, source_ip))
            except Exception as e:
                self._append_log("ERROR", f"Failed to load SRV records: {e}")

        # Load PTR Records
        if self._ptr_records_tree is not None:
            for item in self._ptr_records_tree.get_children():
                self._ptr_records_tree.delete(item)
            try:
                for name, ptrdname, last_seen, source_ip in store.get_all_ptr_records():
                    self._ptr_records_tree.insert("", tk.END, values=(name, ptrdname, last_seen, source_ip))
            except Exception as e:
                self._append_log("ERROR", f"Failed to load PTR records: {e}")

        # Load TXT Records
        if self._txt_records_tree is not None:
            for item in self._txt_records_tree.get_children():
                self._txt_records_tree.delete(item)
            try:
                for name, text, last_seen, source_ip in store.get_all_txt_records():
                    self._txt_records_tree.insert("", tk.END, values=(name, text, last_seen, source_ip))
            except Exception as e:
                self._append_log("ERROR", f"Failed to load TXT records: {e}")

        # Load Queries
        if self._queries_tree is not None:
            for item in self._queries_tree.get_children():
                self._queries_tree.delete(item)
            try:
                for name, qtype, count, last_seen, source_ip in store.get_all_queries():
                    self._queries_tree.insert("", tk.END, values=(name, qtype, count, last_seen, source_ip))
            except Exception as e:
                self._append_log("ERROR", f"Failed to load queries: {e}")

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
        self._ensure_interface_counters()
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
        self._ensure_interface_counters()
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
            counters = self._interface_packet_counts.get(interface.name, {})
            item_id = self._iface_status_tree.insert(
                "",
                tk.END,
                values=(
                    interface.name,
                    listening,
                    ipv4,
                    ipv6,
                    counters.get("rx4", 0),
                    counters.get("tx4", 0),
                    counters.get("rx6", 0),
                    counters.get("tx6", 0),
                ),
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

    def _ensure_interface_counters(self) -> None:
        for interface in self._interfaces:
            self._interface_packet_counts.setdefault(interface.name, {"rx4": 0, "tx4": 0, "rx6": 0, "tx6": 0})

    def _bump_interface_counter(self, interface_name: str, key: str) -> None:
        if interface_name not in self._interface_packet_counts:
            self._interface_packet_counts[interface_name] = {"rx4": 0, "tx4": 0, "rx6": 0, "tx6": 0}
        self._interface_packet_counts[interface_name][key] = self._interface_packet_counts[interface_name].get(key, 0) + 1

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
            self._bump_interface_counter(selected.name, "tx4")
            self._render_interfaces()
        except OSError:
            self._append_log("ERROR", f"service query IPv4 failed on {selected.name}")

    def _send_service_query_ipv6(self) -> None:
        selected = self._get_selected_interface()
        if not self._running or selected is None or not selected.ipv6_addresses:
            self._update_query_buttons_state()
            return
        try:
            self._runtime.send_service_query_ipv6(selected.name)
            self._bump_interface_counter(selected.name, "tx6")
            self._render_interfaces()
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
                    self._bump_interface_counter(interface.name, "tx4")
                except OSError:
                    self._append_log("ERROR", f"service query IPv4 failed on {interface.name}")
            if interface.ipv6_addresses:
                try:
                    self._runtime.send_service_query_ipv6(interface.name)
                    sent_v6 += 1
                    self._bump_interface_counter(interface.name, "tx6")
                except OSError:
                    self._append_log("ERROR", f"service query IPv6 failed on {interface.name}")
        self._render_interfaces()
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
            self._bump_interface_counter(selected.name, "tx4")
            self._render_interfaces()
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
            self._bump_interface_counter(selected.name, "tx6")
            self._render_interfaces()
        except (OSError, ValueError):
            self._append_log("ERROR", f"manual query IPv6 failed on {selected.name}")

    def _poll_events(self) -> None:
        from my_mdns.core.events import ARecordEvent
        while True:
            try:
                event = self._events.get_nowait()
            except Empty:
                break
            if isinstance(event, PacketEvent):
                self._accumulate_stats(event)
                if event.address_family == "IPv4":
                    self._bump_interface_counter(event.capture_interface, "rx4")
                elif event.address_family == "IPv6":
                    self._bump_interface_counter(event.capture_interface, "rx6")
                rr_counts: dict[str, int] = {}
                for rr in event.query_types + event.answer_types:
                    rr_counts[rr] = rr_counts.get(rr, 0) + 1
                formatted_rr_types = ", ".join(
                    f"{rr}" if count == 1 else f"{rr}x{count}"
                    for rr, count in rr_counts.items()
                )

                self._tree.insert(
                    "",
                    0,
                    values=(
                        event.timestamp.strftime("%H:%M:%S.%f")[:-3],
                        f"{event.source_host}:{event.source_port}",
                        event.message_kind,
                        formatted_rr_types,
                        event.byte_count,
                        event.forwarded_count,
                        event.preview_hex,
                    ),
                )
                for item in self._tree.get_children()[300:]:
                    self._tree.delete(item)
                self._render_interfaces()
            elif isinstance(event, ARecordEvent):
                if self._a_records_tree is not None:
                    found_item = None
                    for child in self._a_records_tree.get_children():
                        values = self._a_records_tree.item(child, "values")
                        if values and values[0] == event.name and values[1] == event.ip:
                            found_item = child
                            break
                    if found_item:
                        self._a_records_tree.item(found_item, values=(event.name, event.ip, "Multicast" if event.is_multicast else "Unicast", event.last_seen, event.source_ip))
                        self._a_records_tree.move(found_item, "", 0)
                    else:
                        self._a_records_tree.insert("", 0, values=(event.name, event.ip, "Multicast" if event.is_multicast else "Unicast", event.last_seen, event.source_ip))
            elif isinstance(event, AAAARecordEvent):
                if self._aaaa_records_tree is not None:
                    found_item = None
                    for child in self._aaaa_records_tree.get_children():
                        values = self._aaaa_records_tree.item(child, "values")
                        if values and values[0] == event.name and values[1] == event.ip:
                            found_item = child
                            break
                    if found_item:
                        self._aaaa_records_tree.item(found_item, values=(event.name, event.ip, "Multicast" if event.is_multicast else "Unicast", event.last_seen, event.source_ip))
                        self._aaaa_records_tree.move(found_item, "", 0)
                    else:
                        self._aaaa_records_tree.insert("", 0, values=(event.name, event.ip, "Multicast" if event.is_multicast else "Unicast", event.last_seen, event.source_ip))
            elif isinstance(event, SRVRecordEvent):
                if self._srv_records_tree is not None:
                    found_item = None
                    for child in self._srv_records_tree.get_children():
                        values = self._srv_records_tree.item(child, "values")
                        # Primary key for SRV in DB is (name, target, port)
                        if values and values[0] == event.name and values[1] == event.target and int(values[2]) == event.port:
                            found_item = child
                            break
                    new_values = (event.name, event.target, event.port, event.priority, event.weight, event.last_seen, event.source_ip)
                    if found_item:
                        self._srv_records_tree.item(found_item, values=new_values)
                        self._srv_records_tree.move(found_item, "", 0)
                    else:
                        self._srv_records_tree.insert("", 0, values=new_values)
            elif isinstance(event, PTRRecordEvent):
                if self._ptr_records_tree is not None:
                    found_item = None
                    for child in self._ptr_records_tree.get_children():
                        values = self._ptr_records_tree.item(child, "values")
                        if values and values[0] == event.name and values[1] == event.ptrdname:
                            found_item = child
                            break
                    if found_item:
                        self._ptr_records_tree.item(found_item, values=(event.name, event.ptrdname, event.last_seen, event.source_ip))
                        self._ptr_records_tree.move(found_item, "", 0)
                    else:
                        self._ptr_records_tree.insert("", 0, values=(event.name, event.ptrdname, event.last_seen, event.source_ip))
            elif isinstance(event, TXTRecordEvent):
                if self._txt_records_tree is not None:
                    found_item = None
                    for child in self._txt_records_tree.get_children():
                        values = self._txt_records_tree.item(child, "values")
                        if values and values[0] == event.name and values[1] == event.text:
                            found_item = child
                            break
                    if found_item:
                        self._txt_records_tree.item(found_item, values=(event.name, event.text, event.last_seen, event.source_ip))
                        self._txt_records_tree.move(found_item, "", 0)
                    else:
                        self._txt_records_tree.insert("", 0, values=(event.name, event.text, event.last_seen, event.source_ip))
            elif isinstance(event, QueryEvent):
                if self._queries_tree is not None:
                    found_item = None
                    for child in self._queries_tree.get_children():
                        values = self._queries_tree.item(child, "values")
                        if values and values[0] == event.name and values[1] == event.type:
                            found_item = child
                            break
                    if found_item:
                        # Increment count dynamically since self._event_queue receives 1 increment per query
                        old_count = int(self._queries_tree.item(found_item, "values")[2])
                        new_count = old_count + event.count
                        self._queries_tree.item(found_item, values=(event.name, event.type, new_count, event.last_seen, event.source_ip))
                    else:
                        self._queries_tree.insert("", 0, values=(event.name, event.type, event.count, event.last_seen, event.source_ip))
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

    def _save_column_widths(self, tree_id: str, tree: ttk.Treeview) -> None:
        import json
        from my_mdns.core import store
        widths = {}
        for col in tree["columns"]:
            widths[col] = tree.column(col, "width")
        store.set_ui_setting(f"column_widths_{tree_id}", json.dumps(widths))

    def _load_column_widths(self, tree_id: str, tree: ttk.Treeview) -> None:
        import json
        from my_mdns.core import store
        data = store.get_ui_setting(f"column_widths_{tree_id}")
        if not data:
            return
        try:
            widths = json.loads(data)
            for col, width in widths.items():
                if col in tree["columns"]:
                    tree.column(col, width=width)
        except Exception as e:
            self._append_log("ERROR", f"Failed to load column widths for {tree_id}: {e}")

    def _on_tree_release(self, event: tk.Event, tree_id: str) -> None:
        # Check if resize occurred
        tree = event.widget
        if tree.identify_region(event.x, event.y) == "separator" or True: # Check on every release for now
             self._save_column_widths(tree_id, tree)

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
