"""desktop-seiri package."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("desktop-seiri")
except PackageNotFoundError:
    __version__ = "0+unknown"
