import sys
import os
import argparse
from typing import Dict, List, Any, Optional

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
    import dulwich.porcelain
except ImportError:
    dulwich = None

# --- Common Imports ---

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
        from everything_ipc import scan_by_ipc

# --- Git Info Functions ---

def get_git_info_gitpython(path: str) -> str:
    """Checks if the path is a Git repository using GitPython."""
    if not git:
        return " [GitPython not installed]"
    try:
        # search_parent_directories=False to ensure we create the repo object only if the path ITSELF is a repo.
        # But GitPython's Repo(path) searches upwards by default unless strict checking is done, 
        # but here we rely on it raising InvalidGitRepositoryError if .git is missing in the path or parents.
        # Actually providing search_parent_directories=False is the key.
        repo = git.Repo(path, search_parent_directories=False)
        
        try:
            branch = repo.active_branch.name if not repo.head.is_detached else "DETACHED"
        except:
            branch = "HEADLESS"
        
        status = "dirty" if repo.is_dirty() else "clean"
        return f" <GitPython:{branch} ({status})>"
    except (git.InvalidGitRepositoryError, git.NoSuchPathError):
        return ""
    except Exception as e:
        return f" <GitPython Error: {type(e).__name__}>"

def get_git_info_pygit2(path: str) -> str:
    """Checks if the path is a Git repository using pygit2."""
    if not pygit2:
        return " [pygit2 not installed]"
    try:
        # pygit2.Repository(path) behaves like git_repository_open. 
        # It needs the full path to .git directory usually, or the workdir.
        # Let's try opening. If it fails, it raises GitError.
        repo = pygit2.Repository(path)
        
        # Check if bare?
        if repo.is_bare:
           return " <pygit2:bare>"

        # Get Branch
        branch = "unknown"
        try:
            head = repo.head
            branch = head.shorthand
        except:
            branch = "HEADLESS"

        # Check status
        # repo.status() returns a dictionary of changed files.
        # If empty, it's clean (ignoring untracked files by default? need to check docs, but simple check is enough)
        status = "clean"
        if repo.status():
            status = "dirty"
            
        return f" <pygit2:{branch} ({status})>"
    except Exception:
        # pygit2 raises specialized exceptions, but generic catch is safer for now
        return ""

def get_git_info_dulwich(path: str) -> str:
    """Checks if the path is a Git repository using dulwich."""
    if not dulwich:
        return " [dulwich not installed]"
    try:
        # dulwich.repo.Repo(path)
        repo = dulwich.repo.Repo(path)
        
        # Get Branch
        branch = "unknown"
        try:
            # Read HEAD
            head_ref = repo.refs.read_ref(b'HEAD')
            # If it's a symbolic ref (e.g. ref: refs/heads/master)
            if head_ref.startswith(b'ref: '):
                branch = head_ref.split(b'/')[-1].decode('utf-8')
            else:
                branch = "DETACHED"
        except KeyError:
             branch = "HEADLESS"
        except:
             pass

        # Check status (simplistic)
        # Dulwich's status checking is complex (index vs tree).
        # We'll skip deep status check for speed/complexity and just say "found"
        # Or we can try checking index changes.
        status = "clean?"
        # porcelain.status returns raw status object usually.
        # Let's keep it simple: if we opened the repo, it's a repo.
        
        return f" <dulwich:{branch}>"
    except:
        return ""

def get_git_info(path: str, backend: str) -> str:
    """Dispatch to the appropriate backend."""
    if backend == "gitpython":
        return get_git_info_gitpython(path)
    elif backend == "pygit2":
        return get_git_info_pygit2(path)
    elif backend == "dulwich":
        return get_git_info_dulwich(path)
    else:
        return " [Unknown Backend]"

def find_github_dir(count: int = 20, backend: str = "gitpython"):
    """
    Finds directories that look like GitHub repositories using Everything IPC,
    then verifies them using the specified Git backend.
    """
    print(f"Using Git Backend: {backend}")
    
    # Check if backend is available
    if backend == "gitpython" and not git:
        print("Error: GitPython is not installed.")
        return
    if backend == "pygit2" and not pygit2:
        print("Error: pygit2 is not installed.")
        return
    if backend == "dulwich" and not dulwich:
        print("Error: dulwich is not installed.")
        return

    query = "folder:wfn:GitHub"
    print(f"Searching for potential GitHub directories using query: '{query}'")
    print("-" * 50)

    try:
        results = scan_by_ipc(query, count)
        dirs = results.get("dirs", [])
        
        found_repos = []

        if not dirs:
            print("No folders named 'GitHub' found via Everything.")
        
        for d in dirs:
            path = d['Filename']
            try:
                # Scan subdirectories of the 'GitHub' folder
                with os.scandir(path) as it:
                    for entry in it:
                        if entry.is_dir():
                            info = get_git_info(entry.path, backend)
                            if info:
                                found_repos.append((entry.path, info))
            except PermissionError:
                print(f"Skipping {path}: Permission denied.")
            except Exception as e:
                print(f"Skipping {path}: {e}")

        if found_repos:
            print(f"Found {len(found_repos)} valid Git repositories inside 'GitHub' folders:\n")
            for path, info in found_repos:
                print(f"[REPO] {path}{info}")
        else:
            print("No valid Git repositories found inside the detected 'GitHub' folders.")

    except Exception as e:
        print(f"Search failed: {e}")

def main():
    parser = argparse.ArgumentParser(description="Find GitHub repository directories using Everything and various Git backends.")
    parser.add_argument("--count", "-c", type=int, default=20, help="Maximum number of 'GitHub' folders to scan (default: 20).")
    parser.add_argument("--backend", "-b", choices=["gitpython", "pygit2", "dulwich"], default="gitpython", help="Git backend to use for repository verification.")
    
    args = parser.parse_args()
    find_github_dir(args.count, args.backend)

if __name__ == "__main__":
    main()
