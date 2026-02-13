from .walk import scan as scan_walk
from .scandir import scan as scan_scandir
from .rglob import scan as scan_rglob
from .http import scan as scan_http
from .ipc import scan as scan_ipc
from .types import FileList, FileItem, FileScanner
from .utils import save_to_json, compare_filelists

def scan(target: str) -> FileList:
    """
    Robust scan that runs multiple methods sequentially and validates consistency.
    """
    res_scandir = scan_scandir(target)
    res_walk = scan_walk(target)
    res_rglob = scan_rglob(target)

    # Validate results
    compare_filelists(res_scandir, res_walk, "scandir", "walk")
    compare_filelists(res_scandir, res_rglob, "scandir", "rglob")

    return res_scandir
