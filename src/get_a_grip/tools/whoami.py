import getpass
import os
import sys

def get_effective_user() -> str | None:
    """
    Returns the effective user. On Windows, it attempts to get the sAMAccountName
    (DOMAIN\\username) using the GetUserNameEx API (NameSamCompatible=2).
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

def get_user_principal_name() -> str | None:
    """
    Returns the User Principal Name (typically email format) on Windows
    using the GetUserNameEx API (NameUserPrincipal=1).
    Returns None if not on Windows or if the name cannot be retrieved.
    """
    if sys.platform == "win32":
        try:
            import ctypes
            from ctypes import wintypes
            
            # NameUserPrincipal = 1 (user@domain.com)
            GetUserNameEx = ctypes.windll.secur32.GetUserNameExW
            size = wintypes.ULONG(255)
            buf = ctypes.create_unicode_buffer(size.value)
            
            if GetUserNameEx(1, buf, ctypes.byref(size)):
                return buf.value
        except Exception:
            pass
    return None

def print_whoami() -> None:
    """
    Prints the effective user and principal name if available.
    """
    user = get_effective_user()
    upn = get_user_principal_name()
    if user:
        if upn and upn != user:
            print(f"{user} ({upn})")
        else:
            print(user)
    elif upn:
        print(upn)
