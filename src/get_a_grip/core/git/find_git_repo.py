import os
import argparse
from typing import Dict, Any, List, Optional
from get_a_grip.contracts.git import GitRepoInfo
from .utils import is_bare_repo, get_head_content, get_refs_and_remotes
from get_a_grip.core.everything_ipc import scan_by_ipc

def check_path_info(path: str) -> Optional[GitRepoInfo]:
    """
    Analyzes a potential Git repository path (.git directory or file) 
    and returns a GitRepoInfo structure if valid.
    Returns None if an error occurs.
    """
    repo_dir = path # Initial assumption
    is_file = os.path.isfile(path)
    error = None

    if is_file:
        # It's a .git file (worktree or submodule)
        # We need to resolve the actual gitdir
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read().strip()
                if content.startswith("gitdir:"):
                    rel_git_dir = content[7:].strip()
                    # Resolve relative path from the FILE's directory
                    abs_path = os.path.abspath(os.path.join(os.path.dirname(path), rel_git_dir))
                    repo_dir = abs_path
                    
                    if not os.path.exists(abs_path):
                        error = f"Target repo not found: {abs_path}"
                else:
                    error = "Not a valid gitdir file (no gitdir: prefix)"
        except Exception:
            error = "Error reading .git file"
    else:
        # It's a .git directory
        repo_dir = path

    # Initialize info
    is_bare = False
    is_detached = False
    head = ""
    refs = None
    remotes = None

    if error:
        return None

    is_bare = is_bare_repo(repo_dir)
    
    # Get HEAD content (must be determinable; otherwise treat as error)
    head_path = os.path.join(repo_dir, "HEAD")
    if os.path.exists(head_path):
            try:
                with open(head_path, "r", encoding="utf-8", errors="ignore") as f:
                    head = f.read().strip()
                    if not head:
                        return None
                    if not head.startswith("ref:"):
                        is_detached = True
                    else:
                        is_detached = False
            except Exception:
                return None
    else:
            return None

    # Get Refs and Remotes
    refs, remotes = get_refs_and_remotes(repo_dir)

    return {
        "git_repo_dir": repo_dir,
        "is_bare": is_bare,
        "is_detached": is_detached,
        "head": head,
        "refs": refs,
        "remotes": remotes,
    }


def find_git_repos(count: int = 50) -> List[GitRepoInfo]:
    """
    Searches for Git repositories and returns a list of their info.
    """
    # 1. Search for .git directories
    try:
        results_dirs = scan_by_ipc("folder: exact:.git", count)
        dirs = [d['Filename'] for d in results_dirs.get("dirs", [])]
    except Exception:
        dirs = []

    # 2. Search for .git files
    try:
        results_files = scan_by_ipc("!folder: exact:.git", count)
        files = [f['Filename'] for f in results_files.get("files", [])]
        # In case 'files' contains entries, verify they are files
        files = [f for f in files if os.path.isfile(f)]
    except Exception:
        files = []
    
    candidates = sorted(list(set(dirs + files)))
    
    repos: List[GitRepoInfo] = []
    for path in candidates:
        info = check_path_info(path)
        if info:
            repos.append(info)
    
    return repos

def print_git_repos(repos: List[GitRepoInfo]):
    print(f"Searching for Git repositories (.git directories and configurations)...")
    print("-" * 60)
    print(f"Found {len(repos)} candidates via Everything.\n")

    for info in repos:
        repo = info["git_repo_dir"]
        is_bare = info["is_bare"]
        
        print(f"[REPO] Dir : {repo}")
        
        status = "BARE" if is_bare else "Standard"
        print(f"       Status  : {status}")
        print(f"       HEAD    : {info['head']}")
        if info['is_detached']:
            print(f"       State   : DETACHED")
        
        if info['remotes']:
            print(f"       Remotes : {', '.join(info['remotes'])}")
        if info['refs']:
            print(f"       Refs    : {len(info['refs'])} refs")

        print("")

