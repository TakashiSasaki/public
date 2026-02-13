import ctypes
import os
from typing import Dict, List, Any

# Constants from Everything SDK
EVERYTHING_REQUEST_FILE_NAME = 0x00000001
EVERYTHING_REQUEST_PATH = 0x00000002
EVERYTHING_REQUEST_FULL_PATH_AND_FILE_NAME = 0x00000004
EVERYTHING_REQUEST_EXTENSION = 0x00000008
EVERYTHING_REQUEST_SIZE = 0x00000010
EVERYTHING_REQUEST_DATE_CREATED = 0x00000020
EVERYTHING_REQUEST_DATE_MODIFIED = 0x00000040
EVERYTHING_REQUEST_DATE_ACCESSED = 0x00000080
EVERYTHING_REQUEST_ATTRIBUTES = 0x00000100

def get_dll_path() -> str:
    """Depending on execution context, finds the Everything64.dll."""
    # Priority 1: Relative to current working directory (bin/Everything64.dll)
    cwd_path = os.path.abspath("bin/Everything64.dll")
    if os.path.exists(cwd_path):
        return cwd_path
    
    # Priority 2: Relative to this file (../../../../bin/Everything64.dll)
    # src/get_a_grip/tools/everything_ipc.py -> root/bin/Everything64.dll
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    pkg_path = os.path.join(base_dir, "bin", "Everything64.dll")
    if os.path.exists(pkg_path):
        return pkg_path

    raise FileNotFoundError("Everything64.dll not found in bin/ directory.")

def scan_by_ipc(query: str = "", count: int = 10) -> Dict[str, List[Dict[str, Any]]]:
    """
    Scans using Everything IPC (via DLL) and returns a dict compatible with schema/filelist.json.
    """
    dll_path = get_dll_path()
    try:
        everything_dll = ctypes.WinDLL(dll_path)
    except OSError as e:
        raise RuntimeError(f"Failed to load DLL at {dll_path}: {e}")

    # Define argument and return types
    everything_dll.Everything_SetSearchW.argtypes = [ctypes.c_wchar_p]
    everything_dll.Everything_SetRequestFlags.argtypes = [ctypes.c_uint]
    everything_dll.Everything_SetMax.argtypes = [ctypes.c_uint]
    everything_dll.Everything_QueryW.argtypes = [ctypes.c_bool]
    everything_dll.Everything_QueryW.restype = ctypes.c_bool
    everything_dll.Everything_GetNumResults.restype = ctypes.c_uint
    
    everything_dll.Everything_GetResultFullPathNameW.argtypes = [ctypes.c_uint, ctypes.c_wchar_p, ctypes.c_uint]
    everything_dll.Everything_GetResultSize.argtypes = [ctypes.c_uint, ctypes.POINTER(ctypes.c_ulonglong)]
    everything_dll.Everything_GetResultDateCreated.argtypes = [ctypes.c_uint, ctypes.POINTER(ctypes.c_ulonglong)]
    everything_dll.Everything_GetResultDateModified.argtypes = [ctypes.c_uint, ctypes.POINTER(ctypes.c_ulonglong)]
    everything_dll.Everything_GetResultAttributes.argtypes = [ctypes.c_uint]
    everything_dll.Everything_GetResultAttributes.restype = ctypes.c_uint
    everything_dll.Everything_IsFolderResult.argtypes = [ctypes.c_uint]
    everything_dll.Everything_IsFolderResult.restype = ctypes.c_bool

    # Setup search
    everything_dll.Everything_SetSearchW(query)
    # If count is 0, set to a very large number (effectively unlimited)
    max_results = count if count > 0 else 0xFFFFFFFF
    everything_dll.Everything_SetMax(max_results)
    
    request_flags = (
        EVERYTHING_REQUEST_FULL_PATH_AND_FILE_NAME |
        EVERYTHING_REQUEST_SIZE |
        EVERYTHING_REQUEST_DATE_CREATED | 
        EVERYTHING_REQUEST_DATE_MODIFIED |
        EVERYTHING_REQUEST_ATTRIBUTES
    )
    everything_dll.Everything_SetRequestFlags(request_flags)

    # Execute query
    if not everything_dll.Everything_QueryW(True):
        raise RuntimeError("Everything_QueryW failed. Ensure Everything is running.")

    num_results = everything_dll.Everything_GetNumResults()
    
    files = []
    dirs = []

    # Pre-allocate ctypes buffers
    filename_buffer = ctypes.create_unicode_buffer(2600) # Increased buffer size just in case
    file_size = ctypes.c_ulonglong()
    date_created = ctypes.c_ulonglong()
    date_modified = ctypes.c_ulonglong()

    for i in range(num_results):
        # Get Path
        everything_dll.Everything_GetResultFullPathNameW(i, filename_buffer, 2600)
        filename = filename_buffer.value
        
        # Get Metadata
        everything_dll.Everything_GetResultSize(i, ctypes.byref(file_size))
        everything_dll.Everything_GetResultDateCreated(i, ctypes.byref(date_created))
        everything_dll.Everything_GetResultDateModified(i, ctypes.byref(date_modified))
        attributes = everything_dll.Everything_GetResultAttributes(i)
        is_folder = everything_dll.Everything_IsFolderResult(i)

        item_info = {
            "Filename": filename,
            "Size": file_size.value,
            "Date Modified": str(date_modified.value),
            "Date Created": str(date_created.value),
            "Attributes": attributes
        }

        if is_folder:
            dirs.append(item_info)
        else:
            files.append(item_info)

    return {"files": files, "dirs": dirs}
