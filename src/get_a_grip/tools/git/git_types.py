from typing import TypedDict, Optional, List, Union

class GitRepoInfo(TypedDict):
    """
    Unified information about a detected Git repository or worktree.
    Combines fields from previous GitRepoInfo and GitWorktreeInfo.
    """
    worktree_dir: str
    repo_dir : str # ワークツリーのルートにある .git ディレクトリの場合はそのパス。 .git ファイルの場合はその中に書かれているリポジリのパス
    is_bare: Optional[bool]      # True if it's a bare repository
    is_detached: Optional[bool]  # True if HEAD is detached
    
    # Backend-specific raw output (for debugging/verification)
    gitpython: Optional[str]
    pygit2: Optional[str]
    dulwich: Optional[str]
    
    # Consensus status (None if undetermined or conflicting)
    isClean: Optional[bool]
    hasUntracked: Optional[bool]
    
    headFile: Optional[str] # HEADファイルの中身
    error: Optional[str]

class GitRepoList(TypedDict):
    """
    A collection of Git repository information.
    """
    repos: List[GitRepoInfo]
    count: int

class GitHubRepo(TypedDict):
    """
    Information about a detected GitHub repository.
    This might be merged into GitRepoInfo later, but kept separate for now as it uses a simpler check.
    """
    path: str
    git_info: str

class GitHubRepoList(TypedDict):
    """
    A collection of GitHub repository information.
    """
    repos: List[GitHubRepo]
    count: int
    backend: str
    roots_found: bool
