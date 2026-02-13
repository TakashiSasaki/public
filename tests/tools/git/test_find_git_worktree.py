import os
import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path

from get_a_grip.tools.git.find_git_worktree import (
    find_git_worktrees,
    print_git_worktrees
)

# --- Integration Test using Real Filesystem & Mocked IPC ---

@patch('get_a_grip.tools.git.find_git_worktree.scan_by_ipc')
def test_find_git_worktrees_real_fs(mock_scan, tmp_path, capsys):
    """
    Test finding worktrees with mocked Everything results but real filesystem structures.
    """
    # 1. Setup Filesystem
    
    # Standard Repo
    std_repo = tmp_path / "std_repo"
    std_repo.mkdir()
    (std_repo / ".git").mkdir()
    # HEAD file content
    (std_repo / ".git" / "HEAD").write_text("ref: refs/heads/std-main", encoding="utf-8")
    
    # Worktree Repo
    # We need a 'real' git dir that the worktree points to
    base_repo_git = tmp_path / "base_repo.git"
    base_repo_git.mkdir()
    (base_repo_git / "HEAD").write_text("ref: refs/heads/wt-branch", encoding="utf-8") 
    
    wt_repo = tmp_path / "wt_repo"
    wt_repo.mkdir()
    # .git file pointing to base_repo.git
    rel_to_base = os.path.relpath(base_repo_git, wt_repo)
    (wt_repo / ".git").write_text(f"gitdir: {rel_to_base}", encoding="utf-8")
    
    # 2. Mock Everything Results
    
    def scan_side_effect(query, count):
        if "folder:" in query and "!folder:" not in query:
            # Return directory result
            return {"dirs": [{"Filename": str(std_repo / ".git")}], "files": []}
        else:
            # Return file result
            return {"files": [{"Filename": str(wt_repo / ".git")}], "dirs": []}
            
    mock_scan.side_effect = scan_side_effect
    
    # 3. Mock Git Backends
    # The new function name is get_worktree_status_gitpython
    
    with patch('get_a_grip.tools.git.find_git_worktree.get_worktree_status_gitpython') as mock_gp:
        def gp_side_effect(path):
            p_str = str(path).replace("\\", "/")
            
            if p_str.endswith("/std_repo") or p_str.endswith("std_repo"):
                return {"info": "std-main (clean)", "is_clean": True, "has_untracked": False}
            if p_str.endswith("/wt_repo") or p_str.endswith("wt_repo"):
                return {"info": "wt-branch (clean)", "is_clean": True, "has_untracked": False}
            return None

        mock_gp.side_effect = gp_side_effect

        # Mock pygit2 as well to have "multiple methods" for consensus
        with patch('get_a_grip.tools.git.find_git_worktree.get_worktree_status_pygit2', side_effect=gp_side_effect):
            # We patch pygit2 import check? No need if we mock the function directly.
            # But the module imports pygit2 at top level, if it fails, pygit2 is None.
            # get_worktree_status_pygit2 returns None if pygit2 is None.
            # Since we mock the function call, it should work regardless of import status,
            # unless find_git_worktree logic checks for module existence before calling?
            # get_status_with_timeout calls the function.
            
            # We also need to mock is_bare_repo and other utils if they are used inside find_git_worktrees
            # find_git_worktrees calls:
            # - scan_by_ipc (mocked)
            # - get_worktree_status_* (mocked)
            # - is_bare_repo (imported from utils)
            # - get_head_content (imported from utils)
            # - get_refs_and_remotes (imported from utils)
            
            # Since is_bare_repo and get_head_content use real FS, and we set up real FS,
            # they should work fine without mocking, assuming they handle the paths correctly.
            
            data = find_git_worktrees(count=10, timeout=0)
            print_git_worktrees(data)
            
    captured = capsys.readouterr()
    
    # Check Standard Repo
    assert f"[WORKTREE] {str(std_repo)}" in captured.out
    assert "HEAD      : ref: refs/heads/std-main" in captured.out
    assert "GitPython : std-main (clean)" in captured.out
    assert "Status    : isClean=True hasUntracked=False" in captured.out
    
    # Check Worktree
    assert f"[WORKTREE] {str(wt_repo)}" in captured.out
    assert "HEAD      : ref: refs/heads/wt-branch" in captured.out
    assert "GitPython : wt-branch (clean)" in captured.out
    assert "Status    : isClean=True hasUntracked=False" in captured.out
