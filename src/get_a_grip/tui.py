from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Header, Footer, Input, Button, Label, RichLog, TabbedContent, TabPane
from textual.worker import Worker, WorkerState
import os
from get_a_grip.tools.filelist import scan, save_to_json

# Default UUID from schema/uuid.jsonld
DEFAULT_UUID = "2e985654-ccc3-4141-979b-58d014133d56"

class FilelistTab(Container):
    """UI component for Generating Filelist"""
    
    def compose(self) -> ComposeResult:
        yield Label("📂 Target Directory (Drag & Drop here):")
        yield Input(placeholder="Drop folder here or type path...", id="input_path")
        
        yield Label("🆔 Output UUID (Filename):")
        yield Input(value=DEFAULT_UUID, id="input_uuid")
        
        yield Button("Generate File List", variant="primary", id="btn_run")
        
        yield Label("📝 Log:")
        yield RichLog(id="log_area", highlight=True, markup=True)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_run":
            raw_path = self.query_one("#input_path", Input).value.strip()
            # Windows: Remove surrounding quotes if drag-and-dropped
            path = raw_path.strip('"').strip("'")
            uuid = self.query_one("#input_uuid", Input).value.strip()
            
            if not path:
                self.log_message("[bold red]Error:[/bold red] Please specify a directory.")
                return

            if not os.path.exists(path):
                self.log_message(f"[bold red]Error:[/bold red] Directory not found: {path}")
                return
            
            # Start async worker
            self.run_scan(path, uuid)

    def run_scan(self, path: str, uuid: str) -> None:
        """Runs the scan in a background worker."""
        log = self.query_one("#log_area", RichLog)
        log.write(f"[yellow]Scanning:[/yellow] {path} ...")
        
        def _do_work():
            # NOTE: Do NOT update UI from here. Just do the heavy lifting.
            try:
                # Call the tool logic directly
                data = scan(path)
                
                # Output file is saved INSIDE the target directory
                output_filename = f"{uuid}.json"
                output_path = os.path.join(path, output_filename)
                
                save_to_json(data, output_path)
                return output_path, len(data.get("files", [])), len(data.get("dirs", []))
            except Exception as e:
                # Raise it so on_worker_state_changed catches it
                raise RuntimeError(f"Scan failed: {e}")

        # Launch worker
        self.app.run_worker(_do_work, exclusive=True, thread=True)

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        """Monitor worker state."""
        if event.state == WorkerState.SUCCESS:
            output_path, n_files, n_dirs = event.worker.result
            self.log_message(f"[bold green]Success![/bold green] Found {n_files} files, {n_dirs} dirs.")
            self.log_message(f"Saved to: [underline]{output_path}[/underline]")
        elif event.state == WorkerState.ERROR:
            self.log_message(f"[bold red]Failed:[/bold red] {event.worker.error}")

    def log_message(self, message: str) -> None:
        self.query_one("#log_area", RichLog).write(message)


class GetAGripApp(App):
    CSS = """
    Screen {
        layout: vertical;
    }
    FilelistTab {
        padding: 1;
        layout: vertical;
    }
    Input {
        margin-bottom: 1;
    }
    Button {
        margin-bottom: 2;
        width: 100%;
    }
    RichLog {
        height: 1fr;
        border: solid green;
        background: $surface;
    }
    TabPane {
        padding: 1;
    }
    """

    TITLE = "Get-a-Grip TUI"
    SUB_TITLE = "Directory Scanning Suite"

    def compose(self) -> ComposeResult:
        yield Header()
        with TabbedContent():
            with TabPane("Filelist", id="tab_filelist"):
                yield FilelistTab()
            with TabPane("HTTP Scan", id="tab_http"):
                yield Label("HTTP Scan tool coming soon...")
            with TabPane("IPC Scan", id="tab_ipc"):
                yield Label("IPC Scan tool coming soon...")
        yield Footer()

def main():
    app = GetAGripApp()
    app.run()

if __name__ == "__main__":
    main()
