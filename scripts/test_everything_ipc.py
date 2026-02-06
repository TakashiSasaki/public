import ctypes
import datetime
import struct
import os

# DLLのパス
dll_path = os.path.abspath(r"bin/Everything64.dll")

# 定数定義 (Everything SDK headerより)
EVERYTHING_REQUEST_FILE_NAME = 0x00000001
EVERYTHING_REQUEST_PATH = 0x00000002
EVERYTHING_REQUEST_FULL_PATH_AND_FILE_NAME = 0x00000004
EVERYTHING_REQUEST_EXTENSION = 0x00000008
EVERYTHING_REQUEST_SIZE = 0x00000010
EVERYTHING_REQUEST_DATE_CREATED = 0x00000020
EVERYTHING_REQUEST_DATE_MODIFIED = 0x00000040
EVERYTHING_REQUEST_DATE_ACCESSED = 0x00000080
EVERYTHING_REQUEST_ATTRIBUTES = 0x00000100

def get_filetime(filetime_long):
    """Windows FILETIME (64bit int) を datetime に変換"""
    if filetime_long == 0:
        return "N/A"
    # Windows FILETIME is 100-nanosecond intervals since January 1, 1601 (UTC)
    # UNIX epoch is January 1, 1970
    # Difference is 11644473600 seconds
    try:
        seconds = filetime_long / 10000000
        timestamp = seconds - 11644473600
        return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    except Exception:
         return str(filetime_long)

def main():
    if not os.path.exists(dll_path):
        print(f"Error: DLL not found at {dll_path}")
        return

    try:
        everything_dll = ctypes.WinDLL(dll_path)
    except OSError as e:
        print(f"Failed to load DLL: {e}")
        return

    # 関数の引数と戻り値の型定義
    everything_dll.Everything_SetSearchW.argtypes = [ctypes.c_wchar_p]
    everything_dll.Everything_SetRequestFlags.argtypes = [ctypes.c_uint]
    everything_dll.Everything_QueryW.argtypes = [ctypes.c_bool]
    everything_dll.Everything_QueryW.restype = ctypes.c_bool
    everything_dll.Everything_GetNumResults.restype = ctypes.c_uint
    
    everything_dll.Everything_GetResultFullPathNameW.argtypes = [ctypes.c_uint, ctypes.c_wchar_p, ctypes.c_uint]
    everything_dll.Everything_GetResultSize.argtypes = [ctypes.c_uint, ctypes.POINTER(ctypes.c_ulonglong)]
    everything_dll.Everything_GetResultDateCreated.argtypes = [ctypes.c_uint, ctypes.POINTER(ctypes.c_ulonglong)]
    everything_dll.Everything_GetResultDateModified.argtypes = [ctypes.c_uint, ctypes.POINTER(ctypes.c_ulonglong)]
    everything_dll.Everything_GetResultAttributes.argtypes = [ctypes.c_uint]
    everything_dll.Everything_GetResultAttributes.restype = ctypes.c_uint

    # 検索設定
    search_query = "README.md" # テスト用クエリ
    print(f"Querying for: '{search_query}'...")
    everything_dll.Everything_SetSearchW(search_query)

    # 必要なメタデータを要求
    request_flags = (
        EVERYTHING_REQUEST_FILE_NAME |
        EVERYTHING_REQUEST_PATH |
        EVERYTHING_REQUEST_SIZE |
        EVERYTHING_REQUEST_DATE_CREATED | 
        EVERYTHING_REQUEST_DATE_MODIFIED |
        EVERYTHING_REQUEST_ATTRIBUTES
    )
    everything_dll.Everything_SetRequestFlags(request_flags)

    # クエリ実行 (Wait=True)
    if not everything_dll.Everything_QueryW(True):
        print("Everything_QueryW failed. Is Everything running?")
        return

    num_results = everything_dll.Everything_GetNumResults()
    print(f"Found {num_results} results.")

    # 結果表示 (最大5件)
    max_results = min(num_results, 5)
    
    # バッファの準備
    filename_buffer = ctypes.create_unicode_buffer(260)
    file_size = ctypes.c_ulonglong()
    date_created = ctypes.c_ulonglong()
    date_modified = ctypes.c_ulonglong()

    for i in range(max_results):
        print("-" * 40)
        
        # パス取得
        everything_dll.Everything_GetResultFullPathNameW(i, filename_buffer, 260)
        print(f"Path: {filename_buffer.value}")

        # サイズ取得
        everything_dll.Everything_GetResultSize(i, ctypes.byref(file_size))
        print(f"Size: {file_size.value}")

        # 作成日時取得 (ここが本命！)
        everything_dll.Everything_GetResultDateCreated(i, ctypes.byref(date_created))
        print(f"Date Created (Raw): {date_created.value}")
        print(f"Date Created (Fmt): {get_filetime(date_created.value)}")

        # 更新日時取得
        everything_dll.Everything_GetResultDateModified(i, ctypes.byref(date_modified))
        print(f"Date Modified (Raw): {date_modified.value}")
        print(f"Date Modified (Fmt): {get_filetime(date_modified.value)}")
        
        # 属性取得
        attributes = everything_dll.Everything_GetResultAttributes(i)
        print(f"Attributes: {attributes}")

if __name__ == "__main__":
    main()
