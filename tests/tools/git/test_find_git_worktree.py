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
    
    with patch('get_a_grip.tools.git.find_git_worktree.get_worktree_status_gitpython') as mock_gp:
        def gp_side_effect(path):
            p_str = str(path).replace("\\", "/")
            
            if p_str.endswith("/std_repo") or p_str.endswith("std_repo"):
                return {"is_clean": True, "has_untracked": False}
            if p_str.endswith("/wt_repo") or p_str.endswith("wt_repo"):
                return {"is_clean": True, "has_untracked": False}
            return None

        mock_gp.side_effect = gp_side_effect

        with patch('get_a_grip.tools.git.find_git_worktree.get_worktree_status_pygit2', side_effect=gp_side_effect):
            
            data = find_git_worktrees(count=10, timeout=0)
            print_git_worktrees(data)
            
    captured = capsys.readouterr()
    
    # Check Standard Repo
    assert f"[WORKTREE] {str(std_repo)}" in captured.out
    assert "HEAD      : ref: refs/heads/std-main" in captured.out
    # We no longer print backend-specific info "GitPython : ..."
    # assert "GitPython : std-main (clean)" in captured.out
    assert "Status    : isClean=True hasUntracked=False" in captured.out
    
    # Check Worktree
    assert f"[WORKTREE] {str(wt_repo)}" in captured.out
    assert "HEAD      : ref: refs/heads/wt-branch" in captured.out
    # assert "GitPython : wt-branch (clean)" in captured.out
    assert "Status    : isClean=True hasUntracked=False" in captured.out
