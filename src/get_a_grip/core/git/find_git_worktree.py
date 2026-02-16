import os
import argparse
import concurrent.futures
from typing import Dict, List, Any, Optional, Tuple
from get_a_grip.contracts.git import GitRepoInfo, GitWorktreeInfo
from .utils import (
    get_head_content, 
    get_refs_and_remotes, 
    is_bare_repo, 
    sanitized_git_environment,
    git, 
    pygit2, 
    dulwich
)
from get_a_grip.core.everything_ipc import scan_by_ipc

# --- Git Worktree Status Functions ---

def get_worktree_status_gitpython(path: str) -> Optional[Dict[str, Any]]:
    """Checks if the path is a Git repository using GitPython."""
    if not git:
        return None
    try:
        with sanitized_git_environment():
            # GitPython Repo(path) handles both .git dir and worktree dir automatically.
            repo = git.Repo(path, search_parent_directories=False)

            try:
                branch = repo.active_branch.name if not repo.head.is_detached else "DETACHED"
            except:
                branch = "HEADLESS"

            # is_dirty(untracked_files=False) checks for staged/unstaged changes only
            is_dirty = repo.is_dirty(untracked_files=False)

            # Check for untracked files using ls-files with --directory to avoid recursion into untracked dirs
            untracked = repo.git.ls_files('--others', '--exclude-standard', '--directory', '--no-empty-directory')
            has_untracked = len(untracked.strip()) > 0

            return {
                "is_clean": not is_dirty,
                "has_untracked": has_untracked,
                "valid": True
            }
    except Exception:
        return None

def get_worktree_status_pygit2(path: str) -> Optional[Dict[str, Any]]:
    """Checks if the path is a Git repository using pygit2."""
    if not pygit2:
        return None
    try:
        with sanitized_git_environment():
            # pygit2.Repository(path) works with both worktree and .git dir
            repo = pygit2.Repository(path)

            if repo.is_bare:
               return {
                   "is_clean": True, # Bare is technically clean
                   "has_untracked": False,
                   "valid": True
               }

            # Check status
            status_flags = repo.status()
            is_dirty = False
            has_untracked = False

            for filepath, flags in status_flags.items():
                if flags & pygit2.GIT_STATUS_WT_NEW:
                    has_untracked = True
                if flags & ~pygit2.GIT_STATUS_WT_NEW:
                    is_dirty = True

            return {
                "is_clean": not is_dirty,
                "has_untracked": has_untracked,
                 "valid": True
            }
    except Exception:
        return None

def get_worktree_status_dulwich(path: str) -> Optional[Dict[str, Any]]:
    """Checks if the path is a Git repository using Dulwich."""
    if not dulwich:
        return None
    try:
        with sanitized_git_environment():
            repo = dulwich.repo.Repo(path)

            # Check status using dulwich.porcelain
            is_dirty = False
            has_untracked = False

            try:
                staged, unstaged, untracked = dulwich.porcelain.status(repo)
                if any(staged.values()) or unstaged:
                    is_dirty = True
                if untracked:
                    has_untracked = True
            except Exception:
                # If status fails but repo open succeeded, we might still consider it valid but unknown status?
                # Or just return None if we can't determine status?
                # Let's return None to be safe as per user request (no error info).
                return None

            return {
                "is_clean": not is_dirty,
                "has_untracked": has_untracked,
                 "valid": True
            }

    except Exception:
        return None

def get_status_with_timeout(func, path: str, timeout: float) -> Optional[Dict[str, Any]]:
    """Executes the git status function with a timeout."""
    if timeout <= 0:
        return func(path)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(func, path)
        try:
            return future.result(timeout=timeout)
        except Exception:
            return None

def find_git_worktrees(count: int = 50, timeout: float = 0) -> List[GitWorktreeInfo]:
    """
    Finds git worktrees by searching for .git directories and files.
    Verifies candidates using all available backends.
    """
    query_dirs = "folder: exact:.git"
    query_files = "!folder: exact:.git"

    candidates = []

    # Get .git directories
    try:
        results_dirs = scan_by_ipc(query_dirs, count)
        for d in results_dirs.get("dirs", []):
            git_dir = d['Filename']
            worktree_root = os.path.dirname(git_dir)
            candidates.append(worktree_root)
    except Exception:
        pass

    # Get .git files (for submodules or worktrees)
    try:
        results_files = scan_by_ipc(query_files, count)
        for f in results_files.get("files", []):
            git_file = f['Filename']
            worktree_root = os.path.dirname(git_file)
            candidates.append(worktree_root)
    except Exception:
        pass

    # Remove duplicates
    candidate_paths = sorted(list(set(candidates)))
    
    worktrees: List[GitWorktreeInfo] = []
    
    for path in candidate_paths:
        # 1. Determine Backend Status (for worktree info)
        results = []
        res_gp = get_status_with_timeout(get_worktree_status_gitpython, path, timeout)
        if res_gp: results.append(res_gp)
        
        res_pg = get_status_with_timeout(get_worktree_status_pygit2, path, timeout)
        if res_pg: results.append(res_pg)
        
        res_dw = get_status_with_timeout(get_worktree_status_dulwich, path, timeout)
        if res_dw: results.append(res_dw)

        if not results:
            continue # No valid backend recognized this path

        # Consensus check
        is_clean_votes = [r["is_clean"] for r in results]
        has_untracked_votes = [r["has_untracked"] for r in results]
        
        # Determine consensus
        final_is_clean = False
        if len(set(is_clean_votes)) == 1:
            final_is_clean = is_clean_votes[0]
        else:
             # If conflicting, prioritize 'dirty' (False) to be safe?
             # Or check majority?
             final_is_clean = False 

        final_has_untracked = False
        if len(set(has_untracked_votes)) == 1:
            final_has_untracked = has_untracked_votes[0]
        else:
            final_has_untracked = any(has_untracked_votes) # If any backend sees untracked, say yes?

        # Map to Unified GitRepoInfo
        git_file_check = os.path.join(path, ".git")
        repo_dir = git_file_check # Default assumption
        
        if os.path.isfile(git_file_check):
            try:
                with open(git_file_check, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read().strip()
                        if content.startswith("gitdir:"):
                            rel_git = content[7:].strip()
                            repo_dir = os.path.abspath(os.path.join(path, rel_git))
            except:
                pass
        
        head_content = get_head_content(path)
        is_detached = False
        if head_content and not head_content.startswith("["):
                if not head_content.startswith("ref:"):
                    is_detached = True
        
        refs, remotes = get_refs_and_remotes(path)
        
        repo_info: GitRepoInfo = {
            "git_repo_dir": repo_dir,
            "is_bare": is_bare_repo(path),
            "is_detached": is_detached,
            "head": head_content,
            "refs": refs,
            "remotes": remotes
        }

        worktree_info: GitWorktreeInfo = {
            "git_worktree_dir": path,
            "is_clean": final_is_clean,
            "has_untracked": final_has_untracked,
            "git_repo_info": repo_info
        }

        worktrees.append(worktree_info)
            

    return worktrees

def print_git_worktrees(worktrees: List[GitWorktreeInfo], timeout: float = 0):
    print(f"Searching for Git worktrees...")
    if timeout > 0:
        print(f"Start Timeout: {timeout} seconds")
    else:
        print("Timeout: Disabled (default)")
    print("-" * 50)
    print(f"Found {len(worktrees)} worktrees.\n")

    for info in worktrees:
        print(f"[WORKTREE] {info['git_worktree_dir']}")
        
        repo_info = info['git_repo_info']
        head_info = repo_info['head']
        if repo_info.get('is_detached'):
            head_info += " (DETACHED)"
        
        print(f"  Repo Dir  : {repo_info['git_repo_dir']}")
        print(f"  HEAD      : {head_info}")
        
        if repo_info.get("remotes"):
            print(f"  Remotes   : {', '.join(repo_info['remotes'])}")
        
        status_line = []
        status_line.append(f"isClean={info['is_clean']}")
        status_line.append(f"hasUntracked={info['has_untracked']}")
            
        print(f"  Status    : {' '.join(status_line)}")
        print("")

