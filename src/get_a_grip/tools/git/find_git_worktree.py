import os
import argparse
import concurrent.futures
from typing import Dict, List, Any, Optional, Tuple
from .git_types import GitRepoInfo, GitWorktreeInfo, GitWorktreeList
from .utils import (
    get_head_content, 
    get_refs_and_remotes, 
    is_bare_repo, 
    git, 
    pygit2, 
    dulwich
)
from get_a_grip.tools.everything_ipc import scan_by_ipc

# --- Git Worktree Status Functions ---

def get_worktree_status_gitpython(path: str) -> Optional[Dict[str, Any]]:
    """Checks if the path is a Git repository using GitPython."""
    if not git:
        return None
    try:
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
        
        status = "dirty" if is_dirty else "clean"
        untracked_str = " [untracked]" if has_untracked else ""
        
        return {
            "info": f"{branch} ({status}){untracked_str}",
            "is_clean": not is_dirty,
            "has_untracked": has_untracked
        }
    except (git.InvalidGitRepositoryError, git.NoSuchPathError):
        return None
    except Exception as e:
        return {
            "info": f"Error: {type(e).__name__}",
            "is_clean": None,
            "has_untracked": None
        }

def get_worktree_status_pygit2(path: str) -> Optional[Dict[str, Any]]:
    """Checks if the path is a Git repository using pygit2."""
    if not pygit2:
        return None
    try:
        # pygit2.Repository(path) works with both worktree and .git dir
        repo = pygit2.Repository(path)
        
        if repo.is_bare:
           return {
               "info": "bare",
               "is_clean": True, # Bare is technically clean
               "has_untracked": False
           }

        branch = "unknown"
        try:
            if repo.head_is_detached:
                branch = "DETACHED"
            else:
                head = repo.head
                branch = head.shorthand
        except Exception:
            # Handle unborn branches (empty repo with no commits yet)
            branch = "HEADLESS"
            try:
                is_unborn = False
                try:
                     is_unborn = repo.head_is_unborn
                except:
                     pass
                
                if is_unborn:
                     # Get the symbolic reference target of HEAD (e.g. refs/heads/master)
                     head_ref = repo.lookup_reference("HEAD")
                     target = head_ref.target
                     if target.startswith("refs/heads/"):
                         branch = target[11:]
                     else:
                         branch = target
            except:
                pass

        # Check status
        status_flags = repo.status()
        is_dirty = False
        has_untracked = False
        
        for filepath, flags in status_flags.items():
            if flags & pygit2.GIT_STATUS_WT_NEW:
                has_untracked = True
            if flags & ~pygit2.GIT_STATUS_WT_NEW:
                is_dirty = True
            
        status = "dirty" if is_dirty else "clean"
        untracked_str = " [untracked]" if has_untracked else ""

        return {
            "info": f"{branch} ({status}){untracked_str}",
            "is_clean": not is_dirty,
            "has_untracked": has_untracked
        }
    except Exception as e:
        msg = str(e).lower()
        info = None
        if "cloud file provider" in msg or "クラウド ファイル プロバイダー" in msg:
            info = "[Cloud Error]"
        elif "not owned by current user" in msg:
            info = "[Owner Mismatch]"
        
        if info:
            return {
                "info": info,
                "is_clean": None,
                "has_untracked": None
            }
        return None

def get_worktree_status_dulwich(path: str) -> Optional[Dict[str, Any]]:
    """Checks if the path is a Git repository using Dulwich."""
    if not dulwich:
        return None
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
            return {
                "info": f"{branch} (unknown)",
                "is_clean": None,
                "has_untracked": None
            }

        status = "dirty" if is_dirty else "clean"
        untracked_str = " [untracked]" if has_untracked else ""

        return {
            "info": f"{branch} ({status}){untracked_str}",
            "is_clean": not is_dirty,
            "has_untracked": has_untracked
        }

    except OSError as e:
        if e.errno == 22 and "OneDrive" in path:
            return {
                "info": "[Cloud Error]",
                "is_clean": None,
                "has_untracked": None
            }
        return None
    except Exception:
        return None

def get_status_with_timeout(func, path: str, timeout: float) -> Dict[str, Any]:
    """Executes the git info function with a timeout."""
    if timeout <= 0:
        res = func(path)
        return res if res else {"info": "[None]", "is_clean": None, "has_untracked": None}
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(func, path)
        try:
            res = future.result(timeout=timeout)
            return res if res else {"info": "[None]", "is_clean": None, "has_untracked": None}
        except concurrent.futures.TimeoutError:
            return {"info": "[Timeout]", "is_clean": None, "has_untracked": None}
        except Exception as e:
            return {"info": f"Error: {e}", "is_clean": None, "has_untracked": None}

def find_git_worktrees(count: int = 50, timeout: float = 0) -> GitWorktreeList:
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
        results = {}
        results['gitpython'] = get_status_with_timeout(get_worktree_status_gitpython, path, timeout)
        results['pygit2'] = get_status_with_timeout(get_worktree_status_pygit2, path, timeout)
        results['dulwich'] = get_status_with_timeout(get_worktree_status_dulwich, path, timeout)

        # Consensus check
        is_valid = False
        is_clean_votes = []
        has_untracked_votes = []

        for res in results.values():
             info = res["info"]
             if info and not info.startswith("[") and not info.startswith("Error"):
                 is_valid = True
             
             if res["is_clean"] is not None:
                 is_clean_votes.append(res["is_clean"])
             if res["has_untracked"] is not None:
                 has_untracked_votes.append(res["has_untracked"])
        
        # Determine consensus
        final_is_clean = False # Default to False if undetermined? Or True? 
        # Actually TypedDict says bool, not Optional[bool]. So we must decide.
        # If we can't determine, maybe assume dirty? Or clean?
        # Let's use strict consensus or default to False (dirty/unknown).
        if len(set(is_clean_votes)) == 1 and len(is_clean_votes) >= 1:
            final_is_clean = is_clean_votes[0]
        else:
            final_is_clean = False # Conservative

        final_has_untracked = False
        if len(set(has_untracked_votes)) == 1 and len(has_untracked_votes) >= 1:
            final_has_untracked = has_untracked_votes[0]
        
        if is_valid:
            # Map to Unified GitRepoInfo
            git_file_check = os.path.join(path, ".git")
            repo_dir = git_file_check # Default assumption
            
            # Check if it's a file (.git file) or dir (.git dir) to set repo_dir correctly
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
                "remotes": remotes,
                "gitpython": results['gitpython']["info"],
                "pygit2": results['pygit2']["info"],
                "dulwich": results['dulwich']["info"],
                "error": None
            }

            worktree_info: GitWorktreeInfo = {
                "git_worktree_dir": path,
                "git_repo_dir": repo_dir,
                "is_clean": final_is_clean,
                "has_untracked": final_has_untracked,
                "git_repo_info": repo_info
            }

            worktrees.append(worktree_info)
            
    return {
        "worktrees": worktrees,
        "count": len(worktrees)
    }

def print_git_worktrees(data: GitWorktreeList, timeout: float = 0):
    print(f"Searching for Git worktrees...")
    if timeout > 0:
        print(f"Start Timeout: {timeout} seconds")
    else:
        print("Timeout: Disabled (default)")
    print("-" * 50)
    print(f"Found {data['count']} worktrees.\n")

    for info in data["worktrees"]:
        print(f"[WORKTREE] {info['git_worktree_dir']}")
        
        repo_info = info['git_repo_info']
        head_info = repo_info['head']
        if repo_info['is_detached']:
            head_info += " (DETACHED)"
        
        print(f"  Repo Dir  : {info['git_repo_dir']}")
        print(f"  HEAD      : {head_info}")
        
        if repo_info.get("remotes"):
            print(f"  Remotes   : {', '.join(repo_info['remotes'])}")
        
        # if repo_info.get("refs"):
        #      print(f"  Refs      : {len(repo_info['refs'])} refs found")

        print(f"  GitPython : {repo_info['gitpython']}")
        print(f"  pygit2    : {repo_info['pygit2']}")
        print(f"  Dulwich   : {repo_info['dulwich']}")
        
        status_line = []
        status_line.append(f"isClean={info['is_clean']}")
        status_line.append(f"hasUntracked={info['has_untracked']}")
            
        print(f"  Status    : {' '.join(status_line)}")
        print("")

def main():
    parser = argparse.ArgumentParser(description="Find Git worktrees using Everything and cross-verify with multiple backends.")
    parser.add_argument("--count", "-c", type=int, default=50, help="Maximum number of candidates to scan (default: 50).")
    parser.add_argument("--timeout", "-t", type=float, default=0, help="Timeout in seconds for each backend check (default: 0, 0 for no timeout).")
    parser.add_argument("--list-candidates", "-l", action="store_true", help="List the candidate directories found by Everything, without running Git checks.")
    
    args = parser.parse_args()
    
    if args.list_candidates:
        print("Listing candidates skip... use normal run for data.")
        return

    data = find_git_worktrees(args.count, args.timeout)
    print_git_worktrees(data, args.timeout)

if __name__ == "__main__":
    main()
