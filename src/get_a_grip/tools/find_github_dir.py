import sys
import os
import argparse
from typing import Dict, List, Any, Optional

try:
    import git
except ImportError:
    git = None

# Add current directory to sys.path to ensure we can import the sibling module
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from filelist_ipc import scan_by_ipc
except ImportError:
    # Fallback for package relative import if run as a module
    from .filelist_ipc import scan_by_ipc

def get_git_info(path: str) -> str:
    """Checks if the path is a Git repository root and returns basic info."""
    if not git:
        return ""
    if not os.path.isdir(path):
        return ""
    try:
        # We use search_parent_directories=False because we usually want to know 
        # if the folder ITSELF is a repo root, not if it's inside one.
        repo = git.Repo(path, search_parent_directories=False)
        branch = "unknown"
        try:
            branch = repo.active_branch.name if not repo.head.is_detached else "DETACHED"
        except:
            branch = "HEADLESS"
        
        status = "dirty" if repo.is_dirty() else "clean"
        return f" <GIT:{branch} ({status})>"
    except (git.InvalidGitRepositoryError, git.NoSuchPathError):
        return ""
    except Exception as e:
        return f" <GIT Error: {type(e).__name__}>"

def find_github_dir(count: int = 20):
    """
    Finds directories that look like GitHub repositories.
    It uses Everything IPC to find candidate folders, then checks if they are proper Git repos.
    """
    if not git:
        print("Error: GitPython is not installed. Please install it to use this tool.")
        return

    # Strategy: Find folders named "GitHub" anywhere on the system
    # "folder:wfn:GitHub" -> Folders named exactly "GitHub"
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
            # We are looking for REPOSITORIES inside this GitHub folder.
            # So we list subdirectories of the found 'GitHub' folder.
            try:
                # Use os.scandir for efficiency
                with os.scandir(path) as it:
                    for entry in it:
                        if entry.is_dir():
                            # Check if this subdirectory is a git repo
                            git_info = get_git_info(entry.path)
                            if git_info:
                                found_repos.append((entry.path, git_info))
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
    parser = argparse.ArgumentParser(description="Find GitHub repository directories using Everything and GitPython.")
    parser.add_argument("--count", "-c", type=int, default=20, help="Maximum number of 'GitHub' folders to scan (default: 20).")
    
    args = parser.parse_args()
    find_github_dir(args.count)

if __name__ == "__main__":
    main()
