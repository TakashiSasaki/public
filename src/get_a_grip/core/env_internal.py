import sys
import platform
import os
import site
import importlib.util

def get_python_env_info() -> dict:
    """
    Retrieves information about the current Python execution environment.
    Based on dev-docs/python-env-info.md
    """
    
    # Check for customization hooks
    customization = {}
    for name in ("sitecustomize", "usercustomize"):
        try:
            customization[name] = bool(importlib.util.find_spec(name))
        except (ImportError, AttributeError):
            customization[name] = False

    return {
        "general": {
            "python_executable": sys.executable,
            "python_version": sys.version,
            "platform": sys.platform,
            "system": platform.system(),
            "release": platform.release(),
            "implementation": sys.implementation.name,
            "is_venv": sys.prefix != sys.base_prefix,
            "cwd": os.getcwd(),
        },
        "prefixes": {
            "prefix": sys.prefix,
            "base_prefix": sys.base_prefix,
            "exec_prefix": sys.exec_prefix,
            "base_exec_prefix": sys.base_exec_prefix,
        },
        "paths": {
            "sys_path": sys.path,
        },
        "site": {
            "getsitepackages": site.getsitepackages() if hasattr(site, "getsitepackages") else [],
            "getusersitepackages": site.getusersitepackages(),
            "enable_user_site": site.ENABLE_USER_SITE,
            "user_site": site.USER_SITE,
            "user_base": site.USER_BASE,
            "prefixes": site.PREFIXES,
        },
        "customization": customization,
    }
