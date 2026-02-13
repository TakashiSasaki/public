import os
import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path

from get_a_grip.tools.git.find_git_worktree import (
    get_head_content,
    find_git_worktrees
)

# --- Unit Tests for get_head_content ---

def test_get_head_content_standard(tmp_path):
    git_dir = tmp_path / ".git"
    git_dir.mkdir()
    head_file = git_dir / "HEAD"
    head_file.write_text("ref: refs/heads/main\n", encoding="utf-8")
    
    content = get_head_content(str(tmp_path))
    assert content == "ref: refs/heads/main"

def test_get_head_content_missing_git(tmp_path):
    # No .git directory
    content = get_head_content(str(tmp_path))
    assert content == "[Not Found]"

def test_get_head_content_worktree(tmp_path):
    # Emulate a worktree: .git file pointing to another dir
    real_git_dir = tmp_path / "real_git"
    real_git_dir.mkdir()
    (real_git_dir / "HEAD").write_text("ref: refs/heads/worktree-branch", encoding="utf-8")
    
    wt_root = tmp_path / "wt_root"
    wt_root.mkdir()
    git_file = wt_root / ".git"
    # path in .git file is relative to worktree root
    # Note: On Windows, os.path.relpath might act funny if on different drives, but tmp_path is on same drive.
    rel_path = os.path.relpath(real_git_dir, wt_root)
    git_file.write_text(f"gitdir: {rel_path}\n", encoding="utf-8")
    
    content = get_head_content(str(wt_root))
    assert content == "ref: refs/heads/worktree-branch"

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
    (std_repo / ".git" / "HEAD").write_text("ref: refs/heads/std-main", encoding="utf-8")
    
    # Worktree Repo
    # We need a 'real' git dir that the worktree points to
    base_repo_git = tmp_path / "base_repo.git"
    base_repo_git.mkdir()
    (base_repo_git / "HEAD").write_text("ref: refs/heads/wt-branch", encoding="utf-8") 
    
    wt_repo = tmp_path / "wt_repo"
    wt_repo.mkdir()
    # .git file pointing to base_repo.git
    # Use forward slashes for gitdir potentially, but os.path.join handles separators
    rel_to_base = os.path.relpath(base_repo_git, wt_repo)
    (wt_repo / ".git").write_text(f"gitdir: {rel_to_base}", encoding="utf-8")
    
    # 2. Mock Everything Results
    # find_git_worktrees calls scan_by_ipc twice.
    # First for directories (standard repos), second for files (worktrees).
    
    def scan_side_effect(query, count):
        # query_dirs = "folder: exact:.git"
        if "folder:" in query and "!folder:" not in query:
            # Return directory result
            return {"dirs": [{"Filename": str(std_repo / ".git")}], "files": []}
        else:
            # query_files = "!folder: exact:.git"
            # Return file result
            return {"files": [{"Filename": str(wt_repo / ".git")}], "dirs": []}
            
    mock_scan.side_effect = scan_side_effect
    
    # 3. Mock Git Backends
    # We patch get_git_info_gitpython to return valid info for our paths.
    
    with patch('get_a_grip.tools.git.find_git_worktree.get_git_info_gitpython') as mock_gp:
        def gp_side_effect(path):
            p = Path(path).resolve()
            std_resolved = std_repo.resolve()
            wt_resolved = wt_repo.resolve()
            
        def gp_side_effect(path):
            # Simplify check: avoid complex path resolution issues in mock
            p_str = str(path).replace("\\", "/")
            
            if p_str.endswith("/std_repo") or p_str.endswith("std_repo"):
                return "std-main (clean)"
            if p_str.endswith("/wt_repo") or p_str.endswith("wt_repo"):
                return "wt-branch (clean)"
            return None

        mock_gp.side_effect = gp_side_effect
        
        from get_a_grip.tools.git.find_git_worktree import print_git_worktrees
        # Ensure git is patched as present
        with patch('get_a_grip.tools.git.find_git_worktree.git'):
            data = find_git_worktrees(count=10, timeout=0)
            print_git_worktrees(data)
            
    captured = capsys.readouterr()
    
    # Check Standard Repo
    
    # Check Standard Repo
    # Verify exact path appearance
    assert f"[WORKTREE] {str(std_repo)}" in captured.out
    assert "HEAD      : ref: refs/heads/std-main" in captured.out
    assert "GitPython : std-main (clean)" in captured.out
    
    # Check Worktree
    assert f"[WORKTREE] {str(wt_repo)}" in captured.out
    assert "HEAD      : ref: refs/heads/wt-branch" in captured.out
    assert "GitPython : wt-branch (clean)" in captured.out
