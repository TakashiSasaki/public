import urllib.request
import re
from pathlib import Path
try:
    from importlib import metadata
except ImportError:
    metadata = None

REMOTE_URL = "https://raw.githubusercontent.com/TakashiSasaki/public/refs/heads/llama-cpp-tk/pyproject.toml"

def get_local_version():
    """Attempts to find the local version from package metadata or pyproject.toml."""
    # 1. Try installed package metadata
    try:
        if metadata:
            return metadata.version("llama-cpp-tk")
    except Exception:
        pass
        
    # 2. Try reading local pyproject.toml (dev mode)
    try:
        # Assuming struct: src/llama_cpp_sse/version_check.py
        # root is 3 levels up: ../../../
        root_dir = Path(__file__).resolve().parent.parent.parent
        proj_file = root_dir / "pyproject.toml"
        if proj_file.exists():
            content = proj_file.read_text(encoding="utf-8")
            for line in content.splitlines():
                if line.strip().startswith("version"):
                    # version = "0.1.34"
                    parts = line.split("=")
                    if len(parts) == 2:
                        return parts[1].strip().strip('"').strip("'")
    except Exception:
        pass
        
    return "unknown"

def get_remote_version():
    """Fetches pyproject.toml from GitHub and parses the version."""
    try:
        with urllib.request.urlopen(REMOTE_URL, timeout=5) as response:
            if response.status == 200:
                content = response.read().decode("utf-8")
                # Simple line-based parser for [project] version
                # Note: standard TOML parsers are better but we want zero deps if possible
                for line in content.splitlines():
                    if line.strip().startswith("version"):
                         parts = line.split("=")
                         if len(parts) == 2:
                             return parts[1].strip().strip('"').strip("'")
    except Exception as e:
        print(f"Error fetching remote version: {e}")
        return None
    return None

def check_for_updates():
    """Returns tuple (update_available, local_ver, remote_ver)."""
    local = get_local_version()
    remote = get_remote_version()
    
    if not local or local == "unknown" or not remote:
        return False, local, remote
        
    def parse_version(v_str):
        try:
            return [int(x) for x in v_str.split('.')]
        except:
            return []
            
    is_newer = False
    l_parts = parse_version(local)
    r_parts = parse_version(remote)
    
    if l_parts and r_parts:
        is_newer = r_parts > l_parts
    elif local != remote:
         # Fallback string comparison
         is_newer = remote > local
         
    return is_newer, local, remote
