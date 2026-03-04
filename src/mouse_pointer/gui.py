import tkinter as tk
import json
import importlib.metadata
import platformdirs
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple, Union, Callable
from tkinter import ttk

from mouse_pointer.ui.tabs.editor_tab import build_editor_tab
from mouse_pointer.ui.tabs.export_tab import build_export_tab
from mouse_pointer.ui.tabs.fonts_tab import build_fonts_tab

class CursorGeneratorGUI(tk.Tk):
    def __init__(self):
        super().__init__()

        try:
            version = importlib.metadata.version("mouse-pointer")
        except importlib.metadata.PackageNotFoundError:
            version = "unknown"

        self.title(f"Mouse Cursor Generator v{version}")
        self.geometry("680x560")
        self.configure(padx=10, pady=10)

        # Variables
        self.var_shape = tk.StringVar(value="arrow")
        self.var_size = tk.IntVar(value=32)
        self.var_color = tk.StringVar(value="#800080")       # Default Purple
        self.var_border_color = tk.StringVar(value="#000000") # Default Black
        self.var_border_thickness = tk.IntVar(value=1)
        self.var_tr_text = tk.StringVar(value="")
        self.var_tr_size = tk.IntVar(value=12)
        self.var_mr_text = tk.StringVar(value="")
        self.var_mr_size = tk.IntVar(value=12)
        self.var_caption_text = tk.StringVar(value="")
        self.var_caption_size = tk.IntVar(value=12)
        self.var_caption_color = tk.StringVar(value="#000000") # Default Black
        self.var_caption_bg_color = tk.StringVar(value="#ffffff") # Default White
        self.var_caption_aa = tk.BooleanVar(value=True)
        self.var_caption_outline = tk.BooleanVar(value=False)
        self.var_show_grid = tk.BooleanVar(value=True)
        self.var_drop_shadow = tk.BooleanVar(value=True)

        # SVG Overlay Variables
        self.var_base_name = tk.StringVar(value="")
        self.var_badge1_name = tk.StringVar(value="")
        self.var_badge2_name = tk.StringVar(value="")

        # Pictograms data
        self.pictograms_data = {}

        self.load_settings()
        self.load_pictograms()

        self.create_widgets()
        
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def get_settings_path(self) -> Path:
        """プラットフォーム固有の設定ファイルパスを返す"""
        config_dir = Path(platformdirs.user_config_dir(appname="work.moukaeritai/mouse-pointer", appauthor=False))
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / "editor_settings.json"

    def save_settings(self):
        """現在のエディタ設定をJSONファイルに保存する"""
        settings = {
            "shape": self.var_shape.get(),
            "size": self.var_size.get(),
            "color": self.var_color.get(),
            "border_color": self.var_border_color.get(),
            "border_thickness": self.var_border_thickness.get(),
            "tr_text": self.var_tr_text.get(),
            "tr_size": self.var_tr_size.get(),
            "mr_text": self.var_mr_text.get(),
            "mr_size": self.var_mr_size.get(),
            "caption_text": self.var_caption_text.get(),
            "caption_size": self.var_caption_size.get(),
            "caption_color": self.var_caption_color.get(),
            "caption_bg_color": self.var_caption_bg_color.get(),
            "caption_aa": self.var_caption_aa.get(),
            "caption_outline": self.var_caption_outline.get(),
            "show_grid": self.var_show_grid.get(),
            "drop_shadow": self.var_drop_shadow.get(),
            "base_name": self.var_base_name.get(),
            "badge1_name": self.var_badge1_name.get(),
            "badge2_name": self.var_badge2_name.get(),
        }
        try:
            with open(self.get_settings_path(), "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Failed to save settings: {e}")

    def load_settings(self) -> None:
        """保存されているエディタ設定を読み込んで反映する"""
        path = self.get_settings_path()
        if not path.exists():
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                settings: Dict[str, Any] = json.load(f)
                
                def set_val(var: Union[tk.StringVar, tk.IntVar, tk.BooleanVar], key: str, type_cast: Optional[Callable[[Any], Any]] = None) -> None:
                    if key in settings:
                        val = settings[key]
                        if type_cast:
                            try:
                                if type_cast is bool and isinstance(val, str):
                                    val = val.lower() == "true"
                                else:
                                    val = type_cast(val)
                            except: return
                        var.set(val)

                set_val(self.var_shape, "shape")
                set_val(self.var_size, "size", int)
                set_val(self.var_color, "color")
                set_val(self.var_border_color, "border_color")
                set_val(self.var_border_thickness, "border_thickness", int)
                set_val(self.var_tr_text, "tr_text")
                set_val(self.var_tr_size, "tr_size", int)
                set_val(self.var_mr_text, "mr_text")
                set_val(self.var_mr_size, "mr_size", int)
                set_val(self.var_caption_text, "caption_text")
                set_val(self.var_caption_size, "caption_size", int)
                set_val(self.var_caption_color, "caption_color")
                set_val(self.var_caption_bg_color, "caption_bg_color")
                set_val(self.var_caption_aa, "caption_aa", bool)
                set_val(self.var_caption_outline, "caption_outline", bool)
                set_val(self.var_show_grid, "show_grid", bool)
                set_val(self.var_drop_shadow, "drop_shadow", bool)
                set_val(self.var_base_name, "base_name")
                set_val(self.var_badge1_name, "badge1_name")
                set_val(self.var_badge2_name, "badge2_name")
        except Exception as e:
            print(f"Failed to load settings: {e}")

    def on_close(self):
        """終了時に設定を保存して終了する"""
        self.save_settings()
        self.destroy()

    def load_pictograms(self):
        assets_dir = Path(__file__).parent.parent.parent / "pictogram" / "src" / "assets"
        json_path = assets_dir / "pictograms.json"
        if json_path.exists():
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.pictograms_data = data
            except Exception as e:
                print(f"Failed to load pictograms.json: {e}")

    def hex_to_rgba(self, hex_color: str) -> Tuple[int, int, int, int]:
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 3:
            hex_color = ''.join(c + c for c in hex_color)
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return (r, g, b, 255)

    def create_widgets(self):
        style = ttk.Style(self)
        try:
            style.theme_use('clam')
        except Exception:
            pass

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # ---- Tab 1: Cursor Editor ----
        editor_tab = ttk.Frame(self.notebook, padding=5)
        self.notebook.add(editor_tab, text="  Cursor Editor  ")
        build_editor_tab(self, editor_tab)

        # ---- Tab 2: Vector Font List ----
        vector_fonts_tab = ttk.Frame(self.notebook, padding=5)
        self.notebook.add(vector_fonts_tab, text="  Vector Fonts  ")
        build_fonts_tab(self, vector_fonts_tab, tab_type="vector")

        # ---- Tab 3: Bitmap Font List ----
        bitmap_fonts_tab = ttk.Frame(self.notebook, padding=5)
        self.notebook.add(bitmap_fonts_tab, text="  Bitmap Fonts  ")
        build_fonts_tab(self, bitmap_fonts_tab, tab_type="bitmap")

        # ---- Tab 4: Export Set ----
        export_tab = ttk.Frame(self.notebook, padding=5)
        self.notebook.add(export_tab, text="  Export Set  ")
        build_export_tab(self, export_tab)

def run_gui():
    app = CursorGeneratorGUI()
    app.mainloop()

if __name__ == "__main__":
    run_gui()
