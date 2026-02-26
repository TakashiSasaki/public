from __future__ import annotations

import tkinter as tk
import sqlite3

from . import db, service
from .gui import DesktopSearchApp


def main() -> None:
    conn: sqlite3.Connection | None = None
    root: tk.Tk | None = None
    try:
        conn = db.connect()
        service.initialize_database(conn)

        root = tk.Tk()
        DesktopSearchApp(root, conn)
        root.mainloop()
    except KeyboardInterrupt:
        return
    finally:
        if root is not None:
            try:
                root.destroy()
            except tk.TclError:
                pass
        if conn is not None:
            conn.close()


if __name__ == "__main__":
    main()
