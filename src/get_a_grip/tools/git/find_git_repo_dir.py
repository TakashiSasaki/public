import sys
import os
import argparse
from typing import Dict, Any

# --- Backend Imports ---
try:
    import git
except ImportError:
    git = None

try:
    import pygit2
except ImportError:
    pygit2 = None

try:
    import dulwich.repo
except ImportError:
    dulwich = None

# Add parent directory to sys.path to ensure we can import filelist_ipc from sibling directory
current_file_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_file_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    from get_a_grip.tools.everything_ipc import scan_by_ipc
except ImportError:
    try:
        from ..everything_ipc import scan_by_ipc
    except ImportError:
        # Fallback for standalone script execution
        try:
            from everything_ipc import scan_by_ipc
        except ImportError:
            # Last resort
            scan_by_ipc = None

def is_bare_repo(path: str) -> bool:
    """Checks if a repository at the given path is bare using available backends."""
    # Try pygit2
    if pygit2:
        try:
            repo = pygit2.Repository(path)
            return repo.is_bare
        except:
            pass

    # Try GitPython
    if git:
        try:
            repo = git.Repo(path)
            return repo.bare
        except:
             pass

    # Try Dulwich
    if dulwich:
        try:
            repo = dulwich.repo.Repo(path)
            config = repo.get_config()
            try:
                bare = config.get(b'core', b'bare')
                return bare == b'true'
            except:
                return False
        except:
            pass
            
    # Fallback: Check config file manually
    config_path = os.path.join(path, "config")
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8", errors="ignore") as f:
                if "bare = true" in f.read():
                    return True
        except:
            pass
            
    return False

def check_path_info(path: str) -> Dict[str, Any]:
    info = {
        "path": path,
        "is_file": os.path.isfile(path),
        "target": None,
        "is_bare": False,
        "error": None
    }

    if info["is_file"]:
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read().strip()
                if content.startswith("gitdir:"):
                    rel_path = content[7:].strip()
                    # Resolve relative path from the FILE's directory
                    abs_path = os.path.abspath(os.path.join(os.path.dirname(path), rel_path))
                    info["target"] = abs_path
                    
                    if os.path.exists(abs_path):
                        info["is_bare"] = is_bare_repo(abs_path)
                    else:
                        info["error"] = f"Target not found: {abs_path}"
                else:
                    info["error"] = "Not a valid gitdir file (no gitdir: prefix)"
        except Exception as e:
            info["error"] = str(e)
    else:
        # Directory (.git)
        info["is_bare"] = is_bare_repo(path)

    return info

def find_git_repos(count: int = 50):
    print(f"Searching for Git repositories (.git directories and files)...")
    print("-" * 60)

    # 1. Search for .git directories
    try:
        results_dirs = scan_by_ipc("folder: exact:.git", count)
        dirs = [d['Filename'] for d in results_dirs.get("dirs", [])]
    except Exception as e:
        print(f"Directory search failed: {e}")
        dirs = []

    # 2. Search for .git files
    try:
        results_files = scan_by_ipc("!folder: exact:.git", count)
        files = [f['Filename'] for f in results_files.get("files", [])]
        # In case 'files' contains entries, verify they are files
        files = [f for f in files if os.path.isfile(f)]
    except Exception as e:
        print(f"File search failed: {e}")
        files = []
    
    candidates = sorted(list(set(dirs + files)))
    print(f"Found {len(candidates)} candidates via Everything.\n")

    for path in candidates:
        info = check_path_info(path)
        
        print(f"[REPO] {path}")
        if info["error"]:
             print(f"  Error: {info['error']}")
        else:
             if info["is_file"]:
                 print(f"  Type: Git File (.git)")
                 print(f"  Refers to: {info['target']}")
                 status = "BARE" if info["is_bare"] else "Non-Bare"
                 print(f"  Target Status: {status}")
             else:
                 status = "BARE" if info["is_bare"] else "Non-Bare (Standard)"
                 print(f"  Type: Directory (.git)")
                 print(f"  Status: {status}")
        print("")

def main():
    parser = argparse.ArgumentParser(description="Find Git repositories and check their bare status.")
    parser.add_argument("--count", type=int, default=50, help="Max results from Everything")
    args = parser.parse_args()
    find_git_repos(count=args.count)

if __name__ == "__main__":
    main()
