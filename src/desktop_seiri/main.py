from __future__ import annotations

import tkinter as tk

from . import db, service
from .gui import DesktopSearchApp


def main() -> None:
    conn = db.connect()
    service.initialize_database(conn)

    root = tk.Tk()
    DesktopSearchApp(root, conn)
    root.mainloop()


if __name__ == "__main__":
    main()

