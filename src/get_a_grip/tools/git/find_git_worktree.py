import os
import argparse
import concurrent.futures
from typing import Dict, List, Any, Optional, Tuple
from .git_types import GitWorktreeInfo, GitWorktreeList

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

from get_a_grip.tools.everything_ipc import scan_by_ipc

# --- Git Info Functions ---

def get_git_info_gitpython(path: str) -> Optional[str]:
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
        
        return f"{branch} ({status}){untracked_str}"
    except (git.InvalidGitRepositoryError, git.NoSuchPathError):
        return None
    except Exception as e:
        return f"Error: {type(e).__name__}"

def get_git_info_pygit2(path: str) -> Optional[str]:
    """Checks if the path is a Git repository using pygit2."""
    if not pygit2:
        return None
    try:
        # pygit2.Repository(path) works with both worktree and .git dir
        repo = pygit2.Repository(path)
        
        if repo.is_bare:
           return "bare"

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

        return f"{branch} ({status}){untracked_str}"
    except Exception as e:
        msg = str(e).lower()
        if "cloud file provider" in msg or "クラウド ファイル プロバイダー" in msg:
            return "[Cloud Error]"
        if "not owned by current user" in msg:
            return "[Owner Mismatch]"
        return None

def get_git_info_dulwich(path: str) -> Optional[str]:
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
            return f"{branch} (unknown)"

        status = "dirty" if is_dirty else "clean"
        untracked_str = " [untracked]" if has_untracked else ""

        return f"{branch} ({status}){untracked_str}"

    except OSError as e:
        if e.errno == 22 and "OneDrive" in path:
            return "[Cloud Error]"
        return None
    except Exception:
        return None

def get_git_info_with_timeout(func, path: str, timeout: float) -> str:
    """Executes the git info function with a timeout."""
    if timeout <= 0:
        res = func(path)
        return res if res else "[None]"
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(func, path)
        try:
            res = future.result(timeout=timeout)
            return res if res else "[None]"
        except concurrent.futures.TimeoutError:
            return "[Timeout]"
        except Exception as e:
            return f"Error: {e}"

def get_head_content(path: str) -> str:
    """Reads the content of .git/HEAD if it exists."""
    git_dir = os.path.join(path, ".git")
    head_path = os.path.join(path, ".git", "HEAD")
    
    try:
        try:
            is_dir = os.path.isdir(git_dir)
        except Exception as e:
            return f"[Error checking .git directory '{git_dir}': {e}]"

        if is_dir:
            try:
                if os.path.exists(head_path):
                    with open(head_path, "r", encoding="utf-8", errors="ignore") as f:
                        return f.read().strip()
                return "[HEAD not found]"
            except Exception as e:
                return f"[Error reading HEAD file '{head_path}': {e}]"

        try:
            is_file = os.path.isfile(git_dir)
        except Exception as e:
             return f"[Error checking .git file '{git_dir}': {e}]"

        if is_file:
            try:
                with open(git_dir, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read().strip()
            except Exception as e:
                return f"[Error reading .git file '{git_dir}': {e}]"

            if content.startswith("gitdir:"):
                rel_git_dir = content[7:].strip()
                abs_git_dir = os.path.abspath(os.path.join(path, rel_git_dir))
                real_head_path = os.path.join(abs_git_dir, "HEAD")
                try:
                    if os.path.exists(real_head_path):
                         with open(real_head_path, "r", encoding="utf-8", errors="ignore") as hf:
                            return hf.read().strip()
                    return f"gitdir -> {rel_git_dir} (HEAD not found)"
                except Exception as e:
                    return f"[Error reading linked HEAD '{real_head_path}': {e}]"
            return f"[File: {content[:20]}...]"
        
        return "[Not Found]"
    except Exception as e:
        return f"[Error: {e} (Root Path: {path})]"

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
    candidates = sorted(list(set(candidates)))
    
    worktrees: List[GitWorktreeInfo] = []
    
    for path in candidates:
        results = {}
        results['gitpython'] = get_git_info_with_timeout(get_git_info_gitpython, path, timeout)
        results['pygit2'] = get_git_info_with_timeout(get_git_info_pygit2, path, timeout)
        results['dulwich'] = get_git_info_with_timeout(get_git_info_dulwich, path, timeout)

        # Consensus check
        is_valid = False
        for res in results.values():
             if res and not res.startswith("[") and not res.startswith("Error"):
                 is_valid = True
                 break
        
        if is_valid:
            worktrees.append({
                "path": path,
                "head": get_head_content(path),
                "gitpython": results['gitpython'],
                "pygit2": results['pygit2'],
                "dulwich": results['dulwich']
            })
            
    return {
        "worktrees": worktrees,
        "count": len(worktrees)
    }

def print_git_worktrees(data: GitWorktreeList, timeout: float = 0):
    print(f"Searching for .git directories and files...")
    if timeout > 0:
        print(f"Start Timeout: {timeout} seconds")
    else:
        print("Timeout: Disabled (default)")
    print("-" * 50)
    print(f"Found {data['count']} worktrees.\n")

    for info in data["worktrees"]:
        print(f"[WORKTREE] {info['path']}")
        print(f"  HEAD      : {info['head']}")
        print(f"  GitPython : {info['gitpython']}")
        print(f"  pygit2    : {info['pygit2']}")
        print(f"  Dulwich   : {info['dulwich']}")
        print("")

def main():
    parser = argparse.ArgumentParser(description="Find Git worktrees using Everything and cross-verify with multiple backends.")
    parser.add_argument("--count", "-c", type=int, default=50, help="Maximum number of candidates to scan (default: 50).")
    parser.add_argument("--timeout", "-t", type=float, default=0, help="Timeout in seconds for each backend check (default: 0, 0 for no timeout).")
    parser.add_argument("--list-candidates", "-l", action="store_true", help="List the candidate directories found by Everything, without running Git checks.")
    
    args = parser.parse_args()
    
    if args.list_candidates:
        # Fallback for list-candidates (doesn't return GitWorktreeList easily as it skips checks)
        print("Listing candidates skip... use normal run for data.")
        return

    data = find_git_worktrees(args.count, args.timeout)
    print_git_worktrees(data, args.timeout)

if __name__ == "__main__":
    main()
