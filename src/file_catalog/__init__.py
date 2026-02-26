"""file-catalog package."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("file-catalog")
except PackageNotFoundError:
    __version__ = "0+unknown"

