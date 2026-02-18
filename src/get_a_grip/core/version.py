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

def parse_version(v_str: str) -> tuple[int, ...]:
    """Parse version string into a tuple of integers for comparison."""
    # Handle versions like '0.1.113' or '0.1.113.dev0' or 'unknown'
    # For now, we only focus on the numeric parts
    try:
        parts = re.findall(r'\d+', v_str)
        return tuple(int(p) for p in parts)
    except (ValueError, TypeError):
        return (0,)

def check_for_updates() -> dict:
    """Return a dictionary with local and remote version info."""
    local = get_local_version()
    remote = get_remote_version()
    
    is_dev = local == "dev"
    
    if is_dev:
        up_to_date = True
        status_msg = "Running in development mode"
    elif "unknown" in remote:
        up_to_date = True
        status_msg = "Up to date (offline/error checking remote)"
    else:
        local_v = parse_version(local)
        remote_v = parse_version(remote)
        
        if local_v < remote_v:
            up_to_date = False
            status_msg = "Update available!"
        elif local_v > remote_v:
            up_to_date = True
            status_msg = f"Up to date (newer than remote: v{remote})"
        else:
            up_to_date = True
            status_msg = "Up to date"
            
    return {
        "local": local,
        "remote": remote,
        "is_dev": is_dev,
        "up_to_date": up_to_date,
        "status_msg": status_msg
    }
