import tkinter as tk
from tkinter import ttk
from get_a_grip.core.env_internal import get_python_env_info

class EnvViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("get-a-grip: Python Environment Info")
        self.root.geometry("800x600")
        
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
        
        # We have lists and values here, we'll use a mix
        scrollable_canvas = tk.Canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=scrollable_canvas.yview)
        scrollable_frame = ttk.Frame(scrollable_canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: scrollable_canvas.configure(
                scrollregion=scrollable_canvas.bbox("all")
            )
        )

        scrollable_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        scrollable_canvas.configure(yscrollcommand=scrollbar.set)

        scrollable_canvas.pack(side="left", expand=True, fill="both")
        scrollbar.pack(side="right", fill="y")

        # Basic site info
        site_data = self.info["site"]
        basic_info = {
            "Enable User Site": site_data["enable_user_site"],
            "User Site": site_data["user_site"],
            "User Base": site_data["user_base"],
            "User Site Packages": site_data["getusersitepackages"]
        }
        
        self.create_details_view(scrollable_frame, basic_info)
        
        # List sections
        ttk.Label(scrollable_frame, text="\nSite Packages:", font=("Helvetica", 10, "bold")).pack(anchor="w", padx=5)
        for p in site_data["getsitepackages"]:
            ttk.Label(scrollable_frame, text=f"  • {p}").pack(anchor="w", padx=20)
            
        ttk.Label(scrollable_frame, text="\nSite Prefixes:", font=("Helvetica", 10, "bold")).pack(anchor="w", padx=5)
        for p in site_data["prefixes"]:
            ttk.Label(scrollable_frame, text=f"  • {p}").pack(anchor="w", padx=20)

    def add_customization_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Hooks")
        
        data = {k: "Found" if v else "Not Found" for k, v in self.info["customization"].items()}
        self.create_details_view(frame, data)

    def create_details_view(self, parent, data):
        for i, (key, value) in enumerate(data.items()):
            row_frame = ttk.Frame(parent)
            row_frame.pack(fill="x", padx=5, pady=2)
            
            ttk.Label(row_frame, text=f"{key}:", width=25, anchor="e", font=("Helvetica", 9, "bold")).pack(side="left")
            
            val_label = tk.Text(row_frame, height=1, borderwidth=0, font=("Helvetica", 9))
            val_label.insert("1.0", str(value))
            val_label.configure(state="disabled", background=parent.cget("background"))
            val_label.pack(side="left", fill="x", expand=True, padx=5)

def main():
    root = tk.Tk()
    app = EnvViewerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
