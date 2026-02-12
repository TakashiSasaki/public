from .walk import scan as scan_walk
from .scandir import scan as scan_scandir
from .rglob import scan as scan_rglob
from .http import scan as scan_http
from .ipc import scan as scan_ipc
from .types import FileList, FileItem, FileScanner
from .utils import save_to_json

# Default scanner
scan = scan_scandir
