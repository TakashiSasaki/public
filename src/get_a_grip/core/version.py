"""Version management for get-a-grip."""

import importlib.metadata
import re
from urllib.request import urlopen
from urllib.error import URLError

PYPROJECT_URL = "https://raw.githubusercontent.com/TakashiSasaki/get-a-grip/refs/heads/get-a-grip/pyproject.toml"

def get_local_version() -> str:
    """Return the installed version of get-a-grip."""
    try:
        return importlib.metadata.version("get-a-grip")
    except importlib.metadata.PackageNotFoundError:
        return "dev"

def get_remote_version(timeout: int = 10) -> str:
    """Fetch the latest version from GitHub's pyproject.toml."""
    try:
        with urlopen(PYPROJECT_URL, timeout=timeout) as response:
            content = response.read().decode("utf-8")
        match = re.search(r'^version\s*=\s*"([^"]+)"', content, re.MULTILINE)
        if match:
            return match.group(1)
        return "unknown (parse error)"
    except (URLError, OSError) as e:
        return f"unknown (offline? {e})"

def check_for_updates() -> dict:
    """Return a dictionary with local and remote version info."""
    local = get_local_version()
    remote = get_remote_version()
    
    return {
        "local": local,
        "remote": remote,
        "is_dev": local == "dev",
        "up_to_date": local == remote if local != "dev" else None
    }
