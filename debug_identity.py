import sys
import os
import ctypes
from ctypes import wintypes

# Add src to sys.path
sys.path.append(os.path.join(os.getcwd(), "src"))

from get_a_grip.tools.whoami import get_user_principal_name, get_effective_user

def debug_windows_identity():
    print(f"Platform: {sys.platform}")
    
    if sys.platform != "win32":
        print("Not a Windows system.")
        return

    print("--- Standard Info ---")
    print(f"Effective User (UID): {get_effective_user()}")
    
    print("\n--- Testing GetUserNameExW formats ---")
    
    # Extended Name Formats
    formats = {
        "NameUnknown": 0,
        "NameFullyQualifiedDN": 1, # Actually NameUserPrincipal is 1 in some contexts, but let's check official headers
        "NameSamCompatible": 2,
        "NameDisplay": 3,
        "NameUniqueId": 6,
        "NameCanonical": 7,
        "NameUserPrincipal": 1, # Often 8 or 1 depending on header, but NameUserPrincipal is defined as 1 in many places for this API
        "NameCanonicalEx": 9,
        "NameServicePrincipal": 10,
        "NameDnsDomain": 12
    }
    
    # Correcting common enum values based on secur32.h
    # EXTENDED_NAME_FORMAT:
    # NameUnknown = 0,
    # NameFullyQualifiedDN = 1,
    # NameSamCompatible = 2,
    # NameDisplay = 3,
    # NameUniqueId = 6,
    # NameCanonical = 7,
    # NameUserPrincipal = 8,  <-- Note: NameUserPrincipal is 8 in EXTENDED_NAME_FORMAT enum
    # NameCanonicalEx = 9,
    # NameServicePrincipal = 10,
    # NameDnsDomain = 12
    
    secur32 = ctypes.windll.secur32
    
    actual_formats = [
        ("NameFullyQualifiedDN", 1),
        ("NameSamCompatible", 2),
        ("NameDisplay", 3),
        ("NameUniqueId", 6),
        ("NameCanonical", 7),
        ("NameUserPrincipal", 8), # Try 8 as well
        ("NameCanonicalEx", 9),
        ("NameDnsDomain", 12)
    ]

    for name, fmt in actual_formats:
        size = wintypes.ULONG(255)
        buf = ctypes.create_unicode_buffer(size.value)
        if secur32.GetUserNameExW(fmt, buf, ctypes.byref(size)):
            print(f"{name} ({fmt}): {buf.value}")
        else:
            err = ctypes.GetLastError()
            print(f"{name} ({fmt}): FAILED (Error: {err})")

    print("\n--- get_user_principal_name() result ---")
    os.environ["GET_A_GRIP_DEBUG"] = "1"
    print(f"Result: {get_user_principal_name()}")

if __name__ == "__main__":
    debug_windows_identity()
