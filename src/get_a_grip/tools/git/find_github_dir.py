import os
import argparse
from typing import Dict, List, Any, Optional
from .git_types import GitHubRepo, GitHubRepoList
from .utils import git, pygit2, dulwich, is_bare_repo, get_head_content
from get_a_grip.tools.everything_ipc import scan_by_ipc

# --- Git Info Functions ---

def get_git_info_gitpython(path: str) -> str:
    """Checks if the path is a Git repository using GitPython."""
    if not git:
        return " [GitPython not installed]"
    try:
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
        repo = pygit2.Repository(path)
        if repo.is_bare:
           return " <pygit2:bare>"
        branch = "unknown"
        try:
            if repo.head_is_detached:
                branch = "DETACHED"
            else:
                head = repo.head
                branch = head.shorthand
        except:
            branch = "HEADLESS"
        status = "clean"
        if repo.status():
            status = "dirty"
        return f" <pygit2:{branch} ({status})>"
    except Exception:
        return ""

def get_git_info_dulwich(path: str) -> str:
    """Checks if the path is a Git repository using dulwich."""
    if not dulwich:
        return " [dulwich not installed]"
    try:
        repo = dulwich.repo.Repo(path)
        branch = "unknown"
        try:
             # Read HEAD directly
             head_ref = repo.refs.read_ref(b'HEAD')
             if head_ref.startswith(b'ref: refs/heads/'):
                 branch = head_ref[16:].decode('utf-8')
             elif head_ref.startswith(b'ref: '):
                 branch = head_ref[5:].decode('utf-8')
             else:
                 branch = "DETACHED"
        except (KeyError, Exception):
             branch = "HEADLESS"
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

def find_github_dir(count: int = 20, backend: str = "gitpython") -> GitHubRepoList:
    """
    Finds directories that look like GitHub repositories using Everything IPC.
    """
    query = "folder:wfn:GitHub"
    found_repos: List[GitHubRepo] = []
    roots_found = False

    try:
        results = scan_by_ipc(query, count)
        dirs = results.get("dirs", [])
        if dirs:
            roots_found = True
        
        for d in dirs:
            path = d['Filename']
            try:
                with os.scandir(path) as it:
                    for entry in it:
                        if entry.is_dir():
                            info = get_git_info(entry.path, backend)
                            if info:
                                found_repos.append({"path": entry.path, "git_info": info})
            except (PermissionError, Exception):
                pass
    except Exception:
        pass

    return {
        "repos": found_repos,
        "count": len(found_repos),
        "backend": backend,
        "roots_found": roots_found
    }

def print_github_repos(data: GitHubRepoList):
    print(f"Using Git Backend: {data['backend']}\n")
    print(f"Searching for potential GitHub directories...")
    print("-" * 50)

    if not data["roots_found"]:
        print("No folders named 'GitHub' found via Everything.")
        return

    if not data["repos"]:
        print("No valid Git repositories found inside 'GitHub' folders.")
    else:
        print(f"Found {data['count']} valid Git repositories:\n")
        for repo in data["repos"]:
            print(f"[REPO] {repo['path']}{repo['git_info']}")
    print("")

def main():
    parser = argparse.ArgumentParser(description="Find GitHub repository directories using Everything and various Git backends.")
    parser.add_argument("--count", "-c", type=int, default=20, help="Maximum number of 'GitHub' folders to scan (default: 20).")
    parser.add_argument("--backend", "-b", choices=["gitpython", "pygit2", "dulwich"], default="gitpython", help="Git backend to use for repository verification.")
    
    args = parser.parse_args()
    data = find_github_dir(args.count, args.backend)
    print_github_repos(data)

if __name__ == "__main__":
    main()
