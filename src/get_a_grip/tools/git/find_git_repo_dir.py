import os
import argparse
from typing import Dict, Any, List, Optional
from .git_types import GitRepoInfo, GitRepoList

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

from get_a_grip.tools.everything_ipc import scan_by_ipc

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

def check_path_info(path: str) -> GitRepoInfo:
    info: GitRepoInfo = {
        "worktree_dir": os.path.dirname(path) if os.path.isfile(path) else os.path.dirname(path), # .git directory/file is usually at root
        "repo_dir": path, # Initial assumption, updated below if file
        "is_bare": False,
        "is_detached": None,
        "error": None,
        "headFile": None,
        "gitpython": None,
        "pygit2": None,
        "dulwich": None,
        "isClean": None,
        "hasUntracked": None
    }

    is_file = os.path.isfile(path)

    if is_file:
        # It's a .git file (worktree or submodule)
        # worktree_dir is the directory containing the .git file
        info["worktree_dir"] = os.path.dirname(path)
        
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read().strip()
                if content.startswith("gitdir:"):
                    rel_git_dir = content[7:].strip()
                    # Resolve relative path from the FILE's directory
                    abs_path = os.path.abspath(os.path.join(os.path.dirname(path), rel_git_dir))
                    info["repo_dir"] = abs_path
                    
                    if os.path.exists(abs_path):
                        info["is_bare"] = is_bare_repo(abs_path)
                    else:
                        info["error"] = f"Target repo not found: {abs_path}"
                else:
                    info["error"] = "Not a valid gitdir file (no gitdir: prefix)"
        except Exception as e:
            info["error"] = str(e)
    else:
        # It's a .git directory
        # worktree_dir is the parent of the .git directory
        info["worktree_dir"] = os.path.dirname(path)
        info["repo_dir"] = path
        info["is_bare"] = is_bare_repo(path)

    return info

def find_git_repos(count: int = 50) -> GitRepoList:
    """
    Searches for Git repositories and returns a list of their info.
    """
    # 1. Search for .git directories
    try:
        results_dirs = scan_by_ipc("folder: exact:.git", count)
        dirs = [d['Filename'] for d in results_dirs.get("dirs", [])]
    except Exception as e:
        dirs = []

    # 2. Search for .git files
    try:
        results_files = scan_by_ipc("!folder: exact:.git", count)
        files = [f['Filename'] for f in results_files.get("files", [])]
        # In case 'files' contains entries, verify they are files
        files = [f for f in files if os.path.isfile(f)]
    except Exception as e:
        files = []
    
    candidates = sorted(list(set(dirs + files)))
    
    repos: List[GitRepoInfo] = []
    for path in candidates:
        repos.append(check_path_info(path))
    
    return {
        "repos": repos,
        "count": len(repos)
    }

def print_git_repos(data: GitRepoList):
    print(f"Searching for Git repositories (.git directories and files)...")
    print("-" * 60)
    print(f"Found {data['count']} candidates via Everything.\n")

    for info in data["repos"]:
        worktree = info["worktree_dir"]
        repo = info["repo_dir"]
        is_bare = info["is_bare"]
        
        print(f"[REPO] Worktree: {worktree}")
        print(f"       Git Dir : {repo}")
        
        if info["error"]:
             print(f"       Error   : {info['error']}")
        else:
              status = "BARE" if is_bare else "Standard"
              print(f"       Status  : {status}")
              
        print("")

def main():
    parser = argparse.ArgumentParser(description="Find Git repositories and check their bare status.")
    parser.add_argument("--count", type=int, default=50, help="Max results from Everything")
    args = parser.parse_args()
    data = find_git_repos(count=args.count)
    print_git_repos(data)

if __name__ == "__main__":
    main()
