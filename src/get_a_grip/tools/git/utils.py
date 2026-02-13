import os
import concurrent.futures
from typing import Dict, Any, List, Optional, Tuple

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

def get_refs_and_remotes(path: str) -> Tuple[List[str], List[str]]:
    refs_list = []
    remotes_list = []
    
    # Try GitPython
    if git:
        try:
            repo = git.Repo(path, search_parent_directories=False)
            refs_list = [str(r) for r in repo.references]
            remotes_list = [f"{r.name}: {next(r.urls, 'no-url')}" for r in repo.remotes]
            return refs_list, remotes_list
        except:
            pass
            
    # Try pygit2
    if pygit2:
        try:
            repo = pygit2.Repository(path)
            try:
                refs_list = list(repo.listall_references())
            except:
                refs_list = []
            
            remotes_list = []
            try:
                for remote_name in repo.remotes.listall():
                    try:
                        url = repo.remotes[remote_name].url
                        remotes_list.append(f"{remote_name}: {url}")
                    except:
                        remotes_list.append(f"{remote_name}: [error]")
            except:
                pass
            
            return refs_list, remotes_list
        except:
            pass

    # Try Dulwich
    if dulwich:
        try:
            repo = dulwich.repo.Repo(path)
            refs_list = [r.decode('utf-8', 'ignore') for r in repo.get_refs()]
            config = repo.get_config()
            remotes_list = []
            for section in config.sections():
                if section[0] == b'remote':
                    name = section[1].decode('utf-8', 'ignore')
                    try:
                        url = config.get(section, b'url').decode('utf-8', 'ignore')
                        remotes_list.append(f"{name}: {url}")
                    except:
                        remotes_list.append(f"{name}: [no url]")
            return refs_list, remotes_list
        except:
            pass
            
    return [], []

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

def get_git_info_with_timeout(func, path: str, timeout: float) -> Dict[str, Any]:
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
