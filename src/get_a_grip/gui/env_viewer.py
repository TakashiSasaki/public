import tkinter as tk
from tkinter import ttk
from get_a_grip.core.env_internal import get_python_env_info

FIELD_DESCRIPTIONS = {
    # General
    "python_executable": "Path to the Python interpreter binary.",
    "python_version": "Version of the Python interpreter.",
    "platform": "Underlying platform name (e.g., win32, linux).",
    "system": "Operating system name.",
    "release": "Operating system release version.",
    "implementation": "Python implementation (e.g., CPython, PyPy).",
    "is_venv": "True if running inside a virtual environment.",
    "cwd": "Current working directory of the process.",
    
    # Prefixes
    "prefix": "Installation prefix for platform-independent files.",
    "base_prefix": "Base prefix (if in venv, this is the system Python's prefix).",
    "exec_prefix": "Installation prefix for platform-dependent files.",
    "base_exec_prefix": "Base exec_prefix (if in venv, differs from exec_prefix).",
    
    # Site
    "enable_user_site": "True if user-site packages are enabled.",
    "user_site": "Path to the user-site packages directory.",
    "user_base": "Base directory for user-specific installation.",
    "getusersitepackages": "User site-packages directory (returned by site.getusersitepackages()).",
    
    # Hooks
    "sitecustomize": "Whether the 'sitecustomize' module is importable (customization hook).",
    "usercustomize": "Whether the 'usercustomize' module is importable (customization hook).",
}

class EnvViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("get-a-grip: Python Environment Info")
        self.root.geometry("1000x700")
        
        self.info = get_python_env_info()
        
        self.setup_ui()

    def setup_ui(self):
        # Notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(expand=True, fill="both", padx=10, pady=10)

        # Tabs
        self.add_general_tab(notebook)
        self.add_prefixes_tab(notebook)
        self.add_paths_tab(notebook)
        self.add_site_tab(notebook)
        self.add_customization_tab(notebook)

    def add_general_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="General")
        
        self.create_details_view(frame, self.info["general"])

    def add_prefixes_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Prefixes")
        
        self.create_details_view(frame, self.info["prefixes"])

    def add_paths_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="sys.path")
        
        description_label = ttk.Label(frame, text="List of strings that specifies the search path for modules (sys.path).", padding=5)
        description_label.pack(fill="x")

        text_area = tk.Text(frame, wrap="none")
        text_area.pack(expand=True, fill="both", padx=5, pady=5)
        
        # Scrollbars
        ysb = ttk.Scrollbar(frame, orient="vertical", command=text_area.yview)
        xsb = ttk.Scrollbar(frame, orient="horizontal", command=text_area.xview)
        text_area.configure(yscrollcommand=ysb.set, xscrollcommand=xsb.set)
        
        ysb.pack(side="right", fill="y")
        xsb.pack(side="bottom", fill="x")
        
        for path in self.info["paths"]["sys_path"]:
            text_area.insert("end", f"{path}\n")
        
        text_area.configure(state="disabled")

    def add_site_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Site")
        
        # Split into scalar info (Treeview) and lists (Labels/Text)
        # Using PanedWindow to separate standard info from lists
        paned = ttk.PanedWindow(frame, orient="vertical")
        paned.pack(expand=True, fill="both", padx=5, pady=5)
        
        # Top frame: Basic scalar info
        top_frame = ttk.Frame(paned)
        paned.add(top_frame, weight=1)
        
        site_data = self.info["site"]
        basic_info = {
            "enable_user_site": site_data["enable_user_site"],
            "user_site": site_data["user_site"],
            "user_base": site_data["user_base"],
            "getusersitepackages": site_data["getusersitepackages"]
        }
        self.create_details_view(top_frame, basic_info)
        
        # Bottom frame: Lists
        bottom_frame = ttk.Frame(paned)
        paned.add(bottom_frame, weight=1)
        
        # We use a canvas for scrolling the lists if they are long
        canvas = tk.Canvas(bottom_frame)
        scrollbar = ttk.Scrollbar(bottom_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", expand=True, fill="both")
        scrollbar.pack(side="right", fill="y")
        
        # Site Packages List
        ttk.Label(scrollable_frame, text="\nSite Packages (site.getsitepackages()):", font=("Helvetica", 10, "bold")).pack(anchor="w", padx=5)
        ttk.Label(scrollable_frame, text="List of global site-package directories.", font=("Helvetica", 9, "italic")).pack(anchor="w", padx=5)
        for p in site_data["getsitepackages"]:
            ttk.Label(scrollable_frame, text=f"  • {p}").pack(anchor="w", padx=20)
            
        # Site Prefixes List
        ttk.Label(scrollable_frame, text="\nSite Prefixes (site.PREFIXES):", font=("Helvetica", 10, "bold")).pack(anchor="w", padx=5)
        ttk.Label(scrollable_frame, text="List of prefixes for site-packages.", font=("Helvetica", 9, "italic")).pack(anchor="w", padx=5)
        for p in site_data["prefixes"]:
            ttk.Label(scrollable_frame, text=f"  • {p}").pack(anchor="w", padx=20)

    def add_customization_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Hooks")
        
        data = {k: "Found" if v else "Not Found" for k, v in self.info["customization"].items()}
        self.create_details_view(frame, data)

    def create_details_view(self, parent, data):
        # Create Treeview
        columns = ("key", "value", "description")
        tree = ttk.Treeview(parent, columns=columns, show="headings")
        
        tree.heading("key", text="Key")
        tree.heading("value", text="Value")
        tree.heading("description", text="Description")
        
        tree.column("key", width=150, minwidth=100)
        tree.column("value", width=400, minwidth=200)
        tree.column("description", width=400, minwidth=200)
        
        # Add scrollbars
        vsb = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(parent, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Grid layout for tree and scrollbars
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(0, weight=1)
        
        tree.grid(column=0, row=0, sticky="nsew")
        vsb.grid(column=1, row=0, sticky="ns")
        hsb.grid(column=0, row=1, sticky="ew")
        
        # Insert data
        for key, value in data.items():
            description = FIELD_DESCRIPTIONS.get(key, "")
            tree.insert("", "end", values=(key, str(value), description))

def main():
    root = tk.Tk()
    app = EnvViewerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
