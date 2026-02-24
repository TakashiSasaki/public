from __future__ import annotations

import argparse

from my_mdns.gui.app import MDNSApp


def main() -> None:
    parser = argparse.ArgumentParser(description="my-mdns prototype")
    parser.add_argument(
        "--version",
        action="store_true",
        help="print version and exit",
    )
    args = parser.parse_args()

    if args.version:
        from my_mdns import __version__

        print(__version__)
        return

    app = MDNSApp()
    try:
        app.run()
    except KeyboardInterrupt:
        app.shutdown()


if __name__ == "__main__":
    main()
