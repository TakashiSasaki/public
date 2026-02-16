import unittest
import tkinter as tk
from get_a_grip.gui.env_viewer import EnvViewerApp
import sys

class TestEnvViewer(unittest.TestCase):
    def test_gui_launch(self):
        """
        Verifies that the EnvViewerApp launches without errors.
        This test requires a display environment.
        """
        try:
            root = tk.Tk()
            # Hide window to avoid popping up during tests
            root.withdraw()
            
            app = EnvViewerApp(root)
            
            # Force update to catch layout errors
            root.update()
            
            root.destroy()
        except tk.TclError as e:
            # Handle headless environments (CI/CD)
            if "no display name" in str(e) or "display" in str(e).lower():
                self.skipTest("No display available for GUI test")
            else:
                self.fail(f"GUI launch failed: {e}")
        except Exception as e:
            self.fail(f"GUI launch failed with unexpected error: {e}")

if __name__ == "__main__":
    unittest.main()
