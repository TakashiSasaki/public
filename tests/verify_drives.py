import ctypes
import shutil
import sys

def check_drives():
    print("Checking drives...")
    try:
        bitmask = ctypes.windll.kernel32.GetLogicalDrives()
        for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            if bitmask & 1:
                drive_path = f"{letter}:\\"
                drive_type = ctypes.windll.kernel32.GetDriveTypeW(drive_path)
                
                # DRIVE_FIXED = 3
                type_str = "FIXED" if drive_type == 3 else f"OTHER ({drive_type})"
                print(f"Drive {letter}: Type={type_str}")

                if drive_type == 3:
                    try:
                        usage = shutil.disk_usage(drive_path)
                        total_gb = usage.total / (1024**3)
                        free_gb = usage.free / (1024**3)
                        percent = (usage.used / usage.total) * 100 if usage.total > 0 else 0
                        print(f"  - Total: {total_gb:.2f} GB")
                        print(f"  - Free:  {free_gb:.2f} GB")
                        print(f"  - Usage: {percent:.1f}%")
                    except Exception as e:
                        print(f"  - Error getting usage: {e}")
            bitmask >>= 1
    except Exception as e:
        print(f"Failed to list drives: {e}")

if __name__ == "__main__":
    check_drives()
