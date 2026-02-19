"""
Llama.cpp SSE GUI - A ttk-based graphical interface for running llama.cpp models.

Features:
- Chat tab with model/backend selection and output streaming
- Advanced Settings tab with comprehensive llama.cpp parameter controls
- Environment Info tab showing system capabilities
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import subprocess
import threading
import sys
import os
import platform
from pathlib import Path
import queue
import tempfile

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
DEPS_DIR = Path("deps")
MODELS_DIR = Path("models")

BACKEND_MAP = {
    "cpu": DEPS_DIR / "llama_cpp_cpu" / "llama-cli.exe",
    "cuda": DEPS_DIR / "llama_cpp_cuda" / "llama-cli.exe",
    "vulkan": DEPS_DIR / "llama_cpp_vulkan" / "llama-cli.exe",
}

# Parameter definitions: (flag, label, description, type, default, options/range)
# type: "int", "float", "combo", "bool", "str"
GENERATION_PARAMS = [
    ("--temp", "Temperature", "Controls randomness. Lower = more deterministic, higher = more creative.", "float", 0.8, (0.0, 2.0)),
    ("-c", "Context Size", "Maximum number of tokens the model can see at once (prompt + response).", "combo", "0", ["0 (auto)", "512", "1024", "2048", "4096", "8192", "16384", "32768"]),
    ("-n", "Max Tokens", "Maximum number of tokens to generate. -1 = unlimited.", "int", -1, (-1, 99999)),
    ("-s", "Seed", "Random seed for reproducibility. -1 = random.", "int", -1, (-1, 999999999)),
    ("-ngl", "GPU Layers", "Number of model layers to offload to GPU. Higher = faster but uses more VRAM.", "int", 99, (0, 200)),
    ("-b", "Batch Size", "Logical batch size for prompt processing. Larger = faster prompt eval, more memory.", "int", 2048, (1, 8192)),
    ("-ub", "Micro Batch", "Physical (micro) batch size. Must be ≤ batch size.", "int", 512, (1, 4096)),
    ("-t", "CPU Threads", "Number of CPU threads for generation. -1 = auto.", "int", -1, (-1, 128)),
]

SAMPLING_PARAMS = [
    ("--top-k", "Top-K", "Limits token selection to the K most likely tokens. 0 = disabled.", "int", 40, (0, 1000)),
    ("--top-p", "Top-P (Nucleus)", "Limits tokens to those with cumulative probability ≤ P. 1.0 = disabled.", "float", 0.95, (0.0, 1.0)),
    ("--min-p", "Min-P", "Filters out tokens with probability below P × max_prob. 0.0 = disabled.", "float", 0.05, (0.0, 1.0)),
    ("--typical", "Typical-P", "Locally typical sampling. Selects tokens close to expected information content. 1.0 = disabled.", "float", 1.0, (0.0, 1.0)),
    ("--repeat-penalty", "Repeat Penalty", "Penalizes repeated tokens. 1.0 = disabled, >1.0 = less repetition.", "float", 1.0, (0.0, 3.0)),
    ("--repeat-last-n", "Repeat Window", "How many recent tokens to consider for repeat penalty. 0 = disabled, -1 = ctx_size.", "int", 64, (-1, 4096)),
    ("--presence-penalty", "Presence Penalty", "Penalizes tokens that have appeared at all. 0.0 = disabled.", "float", 0.0, (-2.0, 2.0)),
    ("--frequency-penalty", "Frequency Penalty", "Penalizes tokens proportional to how often they appeared. 0.0 = disabled.", "float", 0.0, (-2.0, 2.0)),
]

MIROSTAT_PARAMS = [
    ("--mirostat", "Mirostat Mode", "Adaptive sampling algorithm. 0 = disabled, 1 = Mirostat, 2 = Mirostat 2.0.", "combo", "0", ["0 (off)", "1", "2"]),
    ("--mirostat-lr", "Mirostat LR (eta)", "Learning rate for Mirostat. Controls how quickly it adapts.", "float", 0.1, (0.0, 1.0)),
    ("--mirostat-ent", "Mirostat Entropy (tau)", "Target entropy (perplexity) for Mirostat. Lower = more focused.", "float", 5.0, (0.0, 20.0)),
]

DRY_PARAMS = [
    ("--dry-multiplier", "DRY Multiplier", "DRY (Don't Repeat Yourself) sampling strength. 0.0 = disabled.", "float", 0.0, (0.0, 5.0)),
    ("--dry-base", "DRY Base", "Base value for DRY penalty calculation.", "float", 1.75, (1.0, 4.0)),
    ("--dry-allowed-length", "DRY Allowed Length", "Minimum sequence length before DRY penalty applies.", "int", 2, (0, 64)),
    ("--dry-penalty-last-n", "DRY Penalty Window", "How many recent tokens to check for DRY. -1 = context size.", "int", -1, (-1, 4096)),
]

DYNAMIC_TEMP_PARAMS = [
    ("--dynatemp-range", "Dynamic Temp Range", "Range for dynamic temperature adjustment. 0.0 = disabled.", "float", 0.0, (0.0, 5.0)),
    ("--dynatemp-exp", "Dynamic Temp Exponent", "Exponent for dynamic temperature scaling.", "float", 1.0, (0.1, 5.0)),
]

XTC_PARAMS = [
    ("--xtc-probability", "XTC Probability", "Probability of applying XTC (eXclude Top Choices). 0.0 = disabled.", "float", 0.0, (0.0, 1.0)),
    ("--xtc-threshold", "XTC Threshold", "Threshold for XTC sampling. 1.0 = disabled.", "float", 0.1, (0.0, 1.0)),
]

ADVANCED_MODEL_PARAMS = [
    ("-fa", "Flash Attention", "Use Flash Attention for faster inference. 'auto' lets llama.cpp decide.", "combo", "auto", ["auto", "on", "off"]),
    ("-ctk", "KV Cache Type K", "Data type for KV cache keys. Lower precision = less memory, slight quality loss.", "combo", "f16", ["f32", "f16", "bf16", "q8_0", "q4_0", "q4_1", "iq4_nl", "q5_0", "q5_1"]),
    ("-ctv", "KV Cache Type V", "Data type for KV cache values. Same trade-off as K cache type.", "combo", "f16", ["f32", "f16", "bf16", "q8_0", "q4_0", "q4_1", "iq4_nl", "q5_0", "q5_1"]),
    ("-sm", "Split Mode", "How to split the model across multiple GPUs.", "combo", "layer", ["none", "layer", "row"]),
    ("--mlock", "Lock in RAM", "Force the OS to keep the model in RAM (prevent swapping).", "bool", False, None),
    ("--no-mmap", "Disable mmap", "Disable memory-mapping the model file. Slower load but may reduce page faults.", "bool", False, None),
    ("--ignore-eos", "Ignore EOS", "Ignore end-of-sequence token and keep generating until the token limit.", "bool", False, None),
    ("--no-display-prompt", "Hide Prompt", "Don't echo the prompt text in the output.", "bool", True, None),
]


# ---------------------------------------------------------------------------
# Helper: Create a labeled parameter widget with tooltip
# ---------------------------------------------------------------------------
def create_param_widget(parent, row, flag, label, description, ptype, default, options):
    """Create a labeled parameter input widget with description tooltip."""
    ttk.Label(parent, text=label + ":", anchor="w").grid(row=row, column=0, sticky="w", padx=(5, 10), pady=3)

    var = None
    widget = None

    if ptype == "int":
        var = tk.IntVar(value=default)
        widget = tk.Spinbox(parent, from_=options[0], to=options[1], textvariable=var, width=10)
    elif ptype == "float":
        var = tk.DoubleVar(value=default)
        widget = tk.Spinbox(parent, from_=options[0], to=options[1], increment=0.05, textvariable=var, width=10, format="%.2f")
    elif ptype == "combo":
        var = tk.StringVar(value=default)
        widget = ttk.Combobox(parent, textvariable=var, values=options, width=15, state="readonly")
    elif ptype == "bool":
        var = tk.BooleanVar(value=default)
        widget = ttk.Checkbutton(parent, variable=var)
    elif ptype == "str":
        var = tk.StringVar(value=default)
        widget = ttk.Entry(parent, textvariable=var, width=20)

    if widget:
        widget.grid(row=row, column=1, sticky="w", padx=5, pady=3)

    # Description label (subtle gray)
    desc_label = ttk.Label(parent, text=description, foreground="gray", wraplength=400, anchor="w", justify="left")
    desc_label.grid(row=row, column=2, sticky="w", padx=(10, 5), pady=3)

    return flag, var, ptype


# ---------------------------------------------------------------------------
# Main Application Class
# ---------------------------------------------------------------------------
class LlamaGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Llama.cpp SSE GUI")
        self.root.geometry("1000x750")
        self.root.minsize(800, 600)

        self.process = None
        self.output_queue = queue.Queue()
        self.is_running = False
        self.param_vars = []  # List of (flag, var, ptype)

        self._create_main_layout()
        self._load_models()
        self._check_queue()

    # -----------------------------------------------------------------------
    # Layout
    # -----------------------------------------------------------------------
    def _create_main_layout(self):
        """Build the entire UI."""
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=5, pady=5)

        # --- Tab 1: Chat ---
        chat_tab = ttk.Frame(notebook)
        notebook.add(chat_tab, text="  Chat  ")
        self._build_chat_tab(chat_tab)

        # --- Tab 2: Advanced Settings ---
        settings_tab = ttk.Frame(notebook)
        notebook.add(settings_tab, text="  Advanced Settings  ")
        self._build_settings_tab(settings_tab)

        # --- Tab 3: Environment Info ---
        env_tab = ttk.Frame(notebook)
        notebook.add(env_tab, text="  Environment Info  ")
        self._build_env_tab(env_tab)

    def _build_chat_tab(self, parent):
        """Build the Chat tab with model selection, output, and input."""
        # --- Quick Config Bar ---
        config_frame = ttk.LabelFrame(parent, text="Quick Configuration", padding=8)
        config_frame.pack(fill="x", padx=8, pady=(8, 4))

        # Row 0: Backend & Model
        ttk.Label(config_frame, text="Backend:").grid(row=0, column=0, sticky="w", padx=5, pady=4)
        self.backend_var = tk.StringVar(value="cuda")
        self.backend_combo = ttk.Combobox(
            config_frame, textvariable=self.backend_var,
            values=list(BACKEND_MAP.keys()), state="readonly", width=10
        )
        self.backend_combo.grid(row=0, column=1, sticky="w", padx=5, pady=4)

        ttk.Label(config_frame, text="Model:").grid(row=0, column=2, sticky="w", padx=5, pady=4)
        self.model_var = tk.StringVar()
        self.model_combo = ttk.Combobox(config_frame, textvariable=self.model_var, state="readonly", width=40)
        self.model_combo.grid(row=0, column=3, sticky="w", padx=5, pady=4, columnspan=3)

        # Row 1: System Prompt (optional)
        ttk.Label(config_frame, text="System Prompt:").grid(row=1, column=0, sticky="nw", padx=5, pady=4)
        self.system_prompt_text = tk.Text(config_frame, height=2, wrap="word", font=("Consolas", 9))
        self.system_prompt_text.grid(row=1, column=1, columnspan=5, sticky="ew", padx=5, pady=4)
        config_frame.columnconfigure(3, weight=1)

        # --- Buttons (pack at bottom first for guaranteed visibility) ---
        btn_frame = ttk.Frame(parent, padding=5)
        btn_frame.pack(side="bottom", fill="x", padx=8, pady=(0, 8))

        self.send_btn = ttk.Button(btn_frame, text="▶ Send (Shift+Enter)", command=self._send_prompt)
        self.send_btn.pack(side="left", padx=5)

        self.stop_btn = ttk.Button(btn_frame, text="■ Stop / New Chat", command=self._stop_process, state="disabled")
        self.stop_btn.pack(side="left", padx=5)

        self.clear_btn = ttk.Button(btn_frame, text="🗑 Clear Log", command=self._clear_log)
        self.clear_btn.pack(side="right", padx=5)

        # --- Input Area (pack at bottom second) ---
        input_frame = ttk.LabelFrame(parent, text="User Input", padding=5)
        input_frame.pack(side="bottom", fill="x", padx=8, pady=(0, 4))

        self.input_text = tk.Text(input_frame, height=4, wrap="word", font=("Consolas", 10))
        self.input_text.pack(fill="x", padx=3, pady=3)
        self.input_text.bind("<Shift-Return>", lambda e: self._send_prompt_event(e))

        # --- Output Area (fills remaining space) ---
        output_frame = ttk.LabelFrame(parent, text="Output / Chat Log", padding=5)
        output_frame.pack(side="top", fill="both", expand=True, padx=8, pady=(4, 0))

        self.output_text = scrolledtext.ScrolledText(
            output_frame, state="disabled", wrap="word", font=("Consolas", 10)
        )
        self.output_text.pack(fill="both", expand=True)

    def _send_prompt_event(self, event):
        self._send_prompt()
        return "break"  # Prevent default newline insertion

    def _build_settings_tab(self, parent):
        """Build the Advanced Settings tab with all llama.cpp parameters."""
        canvas = tk.Canvas(parent, highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas)

        scroll_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Enable mousewheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        # --- Parameter Groups ---
        self._add_param_group(scroll_frame, "Generation", GENERATION_PARAMS)
        self._add_param_group(scroll_frame, "Sampling", SAMPLING_PARAMS)
        self._add_param_group(scroll_frame, "Mirostat", MIROSTAT_PARAMS)
        self._add_param_group(scroll_frame, "DRY (Don't Repeat Yourself)", DRY_PARAMS)
        self._add_param_group(scroll_frame, "Dynamic Temperature", DYNAMIC_TEMP_PARAMS)
        self._add_param_group(scroll_frame, "XTC (eXclude Top Choices)", XTC_PARAMS)
        self._add_param_group(scroll_frame, "Model & Memory", ADVANCED_MODEL_PARAMS)

        # --- Reset Button ---
        reset_btn = ttk.Button(scroll_frame, text="Reset All to Defaults", command=self._reset_defaults)
        reset_btn.pack(pady=10)

    def _add_param_group(self, parent, group_name, params):
        """Add a labeled frame with parameter controls."""
        frame = ttk.LabelFrame(parent, text=group_name, padding=10)
        frame.pack(fill="x", padx=10, pady=5, anchor="nw")

        for i, (flag, label, desc, ptype, default, options) in enumerate(params):
            entry = create_param_widget(frame, i, flag, label, desc, ptype, default, options)
            self.param_vars.append(entry)

    def _build_env_tab(self, parent):
        """Build the Environment Info tab."""
        btn_frame = ttk.Frame(parent, padding=5)
        btn_frame.pack(fill="x", padx=8, pady=5)

        ttk.Button(btn_frame, text="🔄 Refresh", command=self._refresh_env_info).pack(side="left", padx=5)

        self.env_text = scrolledtext.ScrolledText(
            parent, state="disabled", wrap="word", font=("Consolas", 10)
        )
        self.env_text.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        # Auto-load on first display
        self.root.after(100, self._refresh_env_info)

    # -----------------------------------------------------------------------
    # Model Loading
    # -----------------------------------------------------------------------
    def _load_models(self):
        if not MODELS_DIR.exists():
            MODELS_DIR.mkdir(parents=True, exist_ok=True)
        models = [f.name for f in MODELS_DIR.glob("*.gguf")]
        self.model_combo["values"] = models
        if models:
            self.model_combo.set(models[0])
        else:
            self.model_combo.set("(no models found)")

    # -----------------------------------------------------------------------
    # Output Logging
    # -----------------------------------------------------------------------
    def _log(self, message):
        self.output_text.configure(state="normal")
        self.output_text.insert("end", message)
        self.output_text.see("end")
        self.output_text.configure(state="disabled")

    # -----------------------------------------------------------------------
    # Process Management
    # -----------------------------------------------------------------------
    def _send_prompt(self):
        prompt = self.input_text.get("1.0", "end-1c").strip()
        if not prompt:
            return

        self.input_text.delete("1.0", "end")
        self._log(f"\n{'─'*60}\n> {prompt}\n{'─'*60}\n\n")

        # If process is already running, send to stdin (Multi-turn)
        if self.process and self.process.poll() is None:
            try:
                # Append newline to trigger generation
                input_data = prompt + "\n"
                self.process.stdin.write(input_data)
                self.process.stdin.flush()
                return
            except Exception as e:
                self._log(f"\nError sending to process: {e}\n")
                self._stop_process()
                # Fall through to restart if write failed

        # --- Start New Process ---
        backend = self.backend_var.get()
        model_name = self.model_var.get()

        if not model_name or model_name == "(no models found)":
            messagebox.showerror("Error", "Please select a model first.\nDownload one with: uv run download-models all")
            return

        model_path = MODELS_DIR / model_name
        cli_path = BACKEND_MAP.get(backend)

        if not cli_path or not cli_path.exists():
            messagebox.showerror("Error", f"Backend binary not found:\n{cli_path}\nRun: uv run download-bin --backend {backend}")
            return

        # Build command with Conversation Mode enabled
        cmd = [str(cli_path), "-m", str(model_path), "-cnv"]

        # System prompt
        sys_prompt = self.system_prompt_text.get("1.0", "end-1c").strip()
        if sys_prompt:
            sys_file = DEPS_DIR / "temp_system_prompt.txt"
            try:
                with open(sys_file, "w", encoding="utf-8") as f:
                    f.write(sys_prompt)
                cmd.extend(["-sysf", str(sys_file.absolute())])
            except Exception:
                pass

        # Collect all parameter values
        flags_used = set()
        for flag, var, ptype in self.param_vars:
            if flag in flags_used:
                continue
            try:
                val = var.get()
            except tk.TclError:
                continue

            if ptype == "bool":
                if val:
                    cmd.append(flag)
            elif ptype == "combo":
                str_val = str(val).split()[0] if val else ""
                if str_val and str_val != "0": # Skip "0 (auto)" default sometimes
                    cmd.extend([flag, str_val])
            else:
                 # Filter out defaults if needed, but explicit is fine
                cmd.extend([flag, str(val)])
            flags_used.add(flag)

        self.is_running = True
        self._update_ui_state(True)

        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"

        # Start thread
        threading.Thread(target=self._run_command_thread, args=(cmd, env, prompt), daemon=True).start()

    def _run_command_thread(self, cmd, env=None, initial_prompt=None):
        try:
            startupinfo = None
            if sys.platform == "win32":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,            # Line buffered
                universal_newlines=True,
                startupinfo=startupinfo,
                env=env,
            )

            # stderr reader thread
            def _read_stderr(proc, q):
                for line in proc.stderr:
                    if "llama_memory_breakdown_print" in line:
                        q.put("\n" + line)
                    else:
                        q.put(line)

            err_thread = threading.Thread(target=_read_stderr, args=(self.process, self.output_queue), daemon=True)
            err_thread.start()

            # Send initial prompt if provided
            if initial_prompt:
                try:
                    self.process.stdin.write(initial_prompt + "\n")
                    self.process.stdin.flush()
                except Exception as e:
                    self.output_queue.put(f"\nError sending initial prompt: {e}\n")

            # stdout reader
            # Note: For interactive chat, reading line-by-line might wait for newline.
            # reading char-by-char might be smoother for streaming but Python's buffering can be tricky.
            # bufsize=1 means line buffered.
            while True:
                # Read line-by-line is safer for simple implementation, 
                # but might feel laggy if model output doesn't include newlines often.
                # Let's try read(1) loop or readline.
                # Given 'bufsize=1', readline() should work well.
                char = self.process.stdout.read(1)
                if not char and self.process.poll() is not None:
                    break
                if char:
                    self.output_queue.put(char)
            
            self.process.wait()
            err_thread.join(timeout=2)
            self.output_queue.put("\n[Process exited]\n")
        except Exception as e:
            self.output_queue.put(f"\nError: {e}\n")
        finally:
            self.process = None
            self.root.after(0, self._update_ui_state, False)

    def _stop_process(self):
        if self.process:
            self.process.terminate()
            self._log("\n[Stopping process/Ending chat...]\n")
        self._update_ui_state(False)

    def _clear_log(self):
        self.output_text.configure(state="normal")
        self.output_text.delete("1.0", "end")
        self.output_text.configure(state="disabled")

    def _update_ui_state(self, running):
        if running:
            # In multi-turn, we allow sending even if running (to queue next message), 
            # BUT confusingly llama.cpp blocks input while generating.
            # Best to keep "Send" enabled but maybe handle concurrent writes carefully?
            # Actually, standard chat UI allows typing while generating.
            self.send_btn.configure(state="normal") 
            self.stop_btn.configure(state="normal")
        else:
            self.send_btn.configure(state="normal")
            self.stop_btn.configure(state="disabled")
            self.is_running = False

    def _check_queue(self):
        while not self.output_queue.empty():
            line = self.output_queue.get_nowait()
            self._log(line)
        self.root.after(50, self._check_queue)

    # -----------------------------------------------------------------------
    # Advanced Settings: Reset
    # -----------------------------------------------------------------------
    def _reset_defaults(self):
        all_params = (
            GENERATION_PARAMS + SAMPLING_PARAMS + MIROSTAT_PARAMS
            + DRY_PARAMS + DYNAMIC_TEMP_PARAMS + XTC_PARAMS + ADVANCED_MODEL_PARAMS
        )
        defaults = {p[0]: p[4] for p in all_params}
        for flag, var, ptype in self.param_vars:
            if flag in defaults:
                try:
                    var.set(defaults[flag])
                except tk.TclError:
                    pass
        messagebox.showinfo("Reset", "All parameters have been reset to their default values.")

    # -----------------------------------------------------------------------
    # Environment Info
    # -----------------------------------------------------------------------
    def _refresh_env_info(self):
        self.env_text.configure(state="normal")
        self.env_text.delete("1.0", "end")

        lines = []
        lines.append("=" * 60)
        lines.append("  SYSTEM ENVIRONMENT INFORMATION")
        lines.append("=" * 60)

        # Python
        lines.append(f"\n--- Python ---")
        lines.append(f"Version  : {sys.version}")
        lines.append(f"Platform : {platform.platform()}")
        lines.append(f"Arch     : {platform.machine()}")
        lines.append(f"Processor: {platform.processor()}")

        # Models
        lines.append(f"\n--- Models ---")
        if MODELS_DIR.exists():
            models = list(MODELS_DIR.glob("*.gguf"))
            if models:
                for m in models:
                    size_mb = m.stat().st_size / (1024 * 1024)
                    lines.append(f"  {m.name}  ({size_mb:.1f} MB)")
            else:
                lines.append("  (no .gguf models found)")
        else:
            lines.append("  (models/ directory not found)")

        # Backends
        lines.append(f"\n--- Backends ---")
        for name, path in BACKEND_MAP.items():
            status = "✓ Found" if path.exists() else "✗ Not found"
            lines.append(f"  {name:8s} : {status}  ({path})")

        # CUDA
        lines.append(f"\n--- CUDA (nvidia-smi) ---")
        try:
            result = subprocess.run(
                ["nvidia-smi"], capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                for line in result.stdout.splitlines()[:12]:
                    lines.append(f"  {line}")
            else:
                lines.append(f"  nvidia-smi failed: {result.stderr.strip()}")
        except FileNotFoundError:
            lines.append("  nvidia-smi not found (CUDA not available)")
        except Exception as e:
            lines.append(f"  Error: {e}")

        # Vulkan
        lines.append(f"\n--- Vulkan (vulkaninfo) ---")
        try:
            result = subprocess.run(
                ["vulkaninfo"], capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                for line in result.stdout.splitlines()[:12]:
                    lines.append(f"  {line}")
            else:
                lines.append(f"  vulkaninfo failed: {result.stderr.strip()}")
        except FileNotFoundError:
            lines.append("  vulkaninfo not found (Vulkan not available)")
        except Exception as e:
            lines.append(f"  Error: {e}")

        # GPU-related environment variables
        lines.append(f"\n--- GPU-related Environment Variables ---")
        found_any = False
        for key, val in sorted(os.environ.items()):
            if any(k in key.upper() for k in ["CUDA", "VULKAN", "NVIDIA", "AMD", "INTEL", "GPU", "LLAMA"]):
                lines.append(f"  {key} = {val}")
                found_any = True
        if not found_any:
            lines.append("  (none found)")

        # HOME check
        lines.append(f"\n--- Paths ---")
        lines.append(f"  HOME        : {os.environ.get('HOME', '(not set)')}")
        lines.append(f"  USERPROFILE : {os.environ.get('USERPROFILE', '(not set)')}")
        lines.append(f"  CWD         : {os.getcwd()}")

        self.env_text.insert("end", "\n".join(lines))
        self.env_text.configure(state="disabled")


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------
def main():
    root = tk.Tk()
    app = LlamaGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
