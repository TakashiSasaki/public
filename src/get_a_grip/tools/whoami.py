import getpass
import os
import sys

def get_effective_user() -> str | None:
    """
    Returns the effective user. On Windows, it attempts to get the sAMAccountName
    (DOMAIN\\username) using the GetUserNameEx API.
    Returns None if the name cannot be retrieved.
    """
    # Attempt Windows-specific API first
    if sys.platform == "win32":
        try:
            import ctypes
            from ctypes import wintypes
            
            # NameSamCompatible = 2 (DOMAIN\\UserName)
            GetUserNameEx = ctypes.windll.secur32.GetUserNameExW
            size = wintypes.ULONG(255)
            buf = ctypes.create_unicode_buffer(size.value)
            
            if GetUserNameEx(2, buf, ctypes.byref(size)):
                return buf.value
        except Exception:
            pass # Fallback to environment variables

    # Fallback/Linux implementation
    try:
        username = getpass.getuser()
        domain = os.environ.get('USERDOMAIN')
        
        if domain and sys.platform == "win32":
            return f"{domain}\\{username}"
        return username
    except Exception:
        return None

def print_whoami() -> None:
    """
    Prints the effective user.
    """
    user = get_effective_user()
    if user:
        print(user)
