import sys
import os
import argparse
from typing import Dict, List, Any, Optional, Tuple

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
    from get_a_grip.tools.filelist_ipc import scan_by_ipc
except ImportError:
    try:
        from ..filelist_ipc import scan_by_ipc
    except ImportError:
        # Fallback for standalone script execution
        from filelist_ipc import scan_by_ipc

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
        # This prevents hanging on large directories like C:\Users\takas
        # Added --no-empty-directory to align with pygit2/Dulwich behavior (ignore empty untracked dirs)
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
                # Check if it's an unborn branch
                # Note: older pygit2 versions might use is_empty or other flags
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
        
        # pygit2 status flags
        # GIT_STATUS_WT_NEW = 1 << 7  (128) -> Untracked
        # Other flags indicate various types of changes (staged, modified, deleted, etc.)
        
        is_dirty = False
        has_untracked = False
        
        for filepath, flags in status_flags.items():
            if flags & pygit2.GIT_STATUS_WT_NEW:
                has_untracked = True
            # If there are ANY other flags, it's considered dirty (modified/staged/deleted/etc)
            # We use a bitwise AND with the inverse of WT_NEW to check for other bits
            if flags & ~pygit2.GIT_STATUS_WT_NEW:
                is_dirty = True
            
        status = "dirty" if is_dirty else "clean"
        untracked_str = " [untracked]" if has_untracked else ""

        return f"{branch} ({status}){untracked_str}"
    except Exception as e:
        # Detect cloud provider errors (OneDrive, etc)
        # Error msg example: "failed to resolve reference 'HEAD': The cloud file provider is not running."
        msg = str(e).lower()
        if "cloud file provider" in msg or "クラウド ファイル プロバイダー" in msg:
            return "[Cloud Error]"
        # Detect ownership issues (e.g. repo owned by SYSTEM but accessed by user)
        # Error msg example: "repository path 'C:/Users/takas' is not owned by current user"
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
                 # Full branch name (e.g. CFQV/takas)
                 branch = head_ref[16:].decode('utf-8')
             elif head_ref.startswith(b'ref: '):
                 # Other symbolic ref, fallback to last component or full ref minus 'ref: '
                 branch = head_ref[5:].decode('utf-8')
             else:
                 branch = "DETACHED"
        except KeyError:
             branch = "HEADLESS"
        except:
             branch = "HEADLESS"

        # Check status using dulwich.porcelain
        is_dirty = False
        has_untracked = False
        
        try:
            # porcelain.status returns a tuple: (staged, unstaged, untracked)
            # staged is a dict: {'add': [], 'delete': [], 'modify': []}
            # unstaged is a list of modified files
            staged, unstaged, untracked = dulwich.porcelain.status(repo)
            
            if any(staged.values()) or unstaged:
                is_dirty = True
            if untracked:
                has_untracked = True
                
        except Exception:
            # If status check fails, fallback or mark as unknown
            return f"{branch} (unknown)"

        status = "dirty" if is_dirty else "clean"
        untracked_str = " [untracked]" if has_untracked else ""

        return f"{branch} ({status}){untracked_str}"

    except OSError as e:
        # Detect cloud provider errors (OneDrive usually maps to errno 22 'Invalid argument' on access)
        # This is a heuristic, but common for "Files On-Demand" issues.
        if e.errno == 22 and "OneDrive" in path:
            return "[Cloud Error]"
        return None
    except Exception:
        return None

import concurrent.futures

def get_git_info_with_timeout(func, path: str, timeout: float) -> str:
    """Executes the git info function with a timeout."""
    if timeout <= 0:
        return func(path)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(func, path)
        try:
            return future.result(timeout=timeout)
        except concurrent.futures.TimeoutError:
            return " [Timeout]"
        except Exception as e:
            return f"Error: {e}"

def get_head_content(path: str) -> str:
    """Reads the content of .git/HEAD if it exists."""
    git_dir = os.path.join(path, ".git")
    head_path = os.path.join(path, ".git", "HEAD")
    
    try:
        # Check if .git is a directory
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

        # Check if .git is a file (submodule/worktree)
        try:
            is_file = os.path.isfile(git_dir)
        except Exception as e:
             return f"[Error checking .git file '{git_dir}': {e}]"

        if is_file:
            # Read the .git file to find the gitdir
            try:
                with open(git_dir, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read().strip()
            except Exception as e:
                return f"[Error reading .git file '{git_dir}': {e}]"

            if content.startswith("gitdir:"):
                # Resolve relative path
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

def find_git_worktrees(count: int = 50, timeout: float = 0, list_candidates: bool = False):
    """
    Finds git worktrees by searching for .git directories and files.
    Verifies candidates using all available backends.
    """
    
    # 1. Search for .git directories
    # "folder: exact:.git"
    query_dirs = "folder: exact:.git"
    
    # 2. Search for .git files (submodules, worktrees, etc)
    # "!folder: exact:.git"
    query_files = "!folder: exact:.git"

    print(f"Searching for .git directories and files...")
    if timeout > 0:
        print(f"Start Timeout: {timeout} seconds")
    else:
        print("Timeout: Disabled (default)")
    print("-" * 50)

    candidates = []

    # Get .git directories
    try:
        results_dirs = scan_by_ipc(query_dirs, count)
        for d in results_dirs.get("dirs", []):
            # The worktree root is usually the parent of the .git directory
            git_dir = d['Filename']
            worktree_root = os.path.dirname(git_dir)
            candidates.append(worktree_root)
    except Exception as e:
        print(f"Directory search failed: {e}")

    # Get .git files (for submodules or worktrees)
    try:
        results_files = scan_by_ipc(query_files, count)
        for f in results_files.get("files", []):
             # For a .git file, it usually points to the git dir, but the file itself is in the worktree root
            git_file = f['Filename']
            worktree_root = os.path.dirname(git_file)
            candidates.append(worktree_root)
    except Exception as e:
        print(f"File search failed: {e}")

    # Remove duplicates
    candidates = sorted(list(set(candidates)))

    print(f"Found {len(candidates)} unique candidates via Everything.\n")
    
    if list_candidates:
        print("Candidates:")
        for path in candidates:
            print(f"  {path}")
        return

    for path in candidates:
        results = {}
        
        # Check with GitPython
        if git:
            results['gitpython'] = get_git_info_with_timeout(get_git_info_gitpython, path, timeout)
        else:
             results['gitpython'] = "[Not Installed]"

        # Check with pygit2
        if pygit2:
            results['pygit2'] = get_git_info_with_timeout(get_git_info_pygit2, path, timeout)
        else:
            results['pygit2'] = "[Not Installed]"

        # Check with dulwich
        if dulwich:
            results['dulwich'] = get_git_info_with_timeout(get_git_info_dulwich, path, timeout)
        else:
            results['dulwich'] = "[Not Installed]"

        # Consensus check
        # We consider it a valid worktree if AT LEAST ONE backend returns a valid result (not None and not Timeout/Error).
        is_valid = False
        for b, res in results.items():
             if res and not res.startswith("[") and not res.startswith("Error"):
                 is_valid = True
                 break
        
        if is_valid:
            head_content = get_head_content(path)
            print(f"[WORKTREE] {path}")
            print(f"  HEAD      : {head_content}")
            print(f"  GitPython : {results['gitpython']}")
            print(f"  pygit2    : {results['pygit2']}")
            print(f"  Dulwich   : {results['dulwich']}")
            print("")

def main():
    parser = argparse.ArgumentParser(description="Find Git worktrees using Everything and cross-verify with multiple backends.")
    parser.add_argument("--count", "-c", type=int, default=50, help="Maximum number of candidates to scan (default: 50).")
    parser.add_argument("--timeout", "-t", type=float, default=0, help="Timeout in seconds for each backend check (default: 0, 0 for no timeout).")
    parser.add_argument("--list-candidates", "-l", action="store_true", help="List the candidate directories found by Everything, without running Git checks.")
    
    args = parser.parse_args()
    find_git_worktrees(args.count, args.timeout, args.list_candidates)

if __name__ == "__main__":
    main()
