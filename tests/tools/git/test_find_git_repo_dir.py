import os
import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path

from get_a_grip.tools.git.find_git_repo_dir import (
    is_bare_repo,
    check_path_info,
    find_git_repos
)

# Use patch to control libraries
@patch('get_a_grip.tools.git.find_git_repo_dir.git')
def test_is_bare_repo_gitpython(mock_git):
    # Mock GitPython Repo
    mock_repo = MagicMock()
    mock_repo.bare = True
    mock_git.Repo.return_value = mock_repo
    
    # Should be True
    assert is_bare_repo("some/path") is True
    
    mock_repo.bare = False
    assert is_bare_repo("some/path") is False

# check_path_info integration with temp fs
def test_check_path_info_dir_non_bare(tmp_path):
    # Setup standard .git dir
    git_dir = tmp_path / ".git"
    git_dir.mkdir()
    # Mock is_bare_repo return using patch
    with patch('get_a_grip.tools.git.find_git_repo_dir.is_bare_repo', return_value=False):
        info = check_path_info(str(git_dir))
        assert info["is_file"] is False
        assert info["is_bare"] is False

def test_check_path_info_dir_bare(tmp_path):
    # Setup bare repo dir (name usually ends in .git)
    bare_dir = tmp_path / "repo.git"
    bare_dir.mkdir()
    with patch('get_a_grip.tools.git.find_git_repo_dir.is_bare_repo', return_value=True):
        info = check_path_info(str(bare_dir))
        assert info["is_file"] is False
        assert info["is_bare"] is True

def test_check_path_info_file(tmp_path):
    # Setup .git file
    wt_root = tmp_path / "wt"
    wt_root.mkdir()
    git_file = wt_root / ".git"
    # Point to a fake existing dir
    real_git = tmp_path / "real.git"
    real_git.mkdir()
    
    # Note: relpath relies on current dir usually, but os.path.relpath(target, start) works fine
    rel_path = os.path.relpath(real_git, wt_root)
    git_file.write_text(f"gitdir: {rel_path}", encoding="utf-8")
    
    # Mock logic that checking the *target* repo
    with patch('get_a_grip.tools.git.find_git_repo_dir.is_bare_repo', return_value=False):
        info = check_path_info(str(git_file))
        assert info["is_file"] is True
        assert info["is_bare"] is False
        assert info["target"] is not None

@patch('get_a_grip.tools.git.find_git_repo_dir.scan_by_ipc')
def test_find_git_repos_integration(mock_scan, tmp_path, capsys):
    # Setup
    # 1. Non-Bare (.git dir)
    nb_root = tmp_path / "nb_root"
    nb_root.mkdir()
    nb_git = nb_root / ".git"
    nb_git.mkdir()
    
    # 2. Bare (bare.git dir)
    bare_git = tmp_path / "bare.git"
    bare_git.mkdir()
    
    # 3. Worktree (.git file)
    wt_root = tmp_path / "wt_root"
    wt_root.mkdir()
    wt_git = wt_root / ".git"
    # Point to nb_git
    rel_path = os.path.relpath(nb_git, wt_root)
    wt_git.write_text(f"gitdir: {rel_path}", encoding="utf-8")
    
    # Mock Everything
    def scan_side_effect(query, count):
        if "folder:" in query and "!folder:" not in query:
             return {"dirs": [{"Filename": str(nb_git)}, {"Filename": str(bare_git)}], "files": []}
        else:
             return {"files": [{"Filename": str(wt_git)}], "dirs": []}
    mock_scan.side_effect = scan_side_effect
    
    # Mock is_bare_repo
    def bare_side_effect(path):
        p_str = str(path).replace("\\", "/")
        if p_str.endswith(".git") and "nb_root" in p_str:
            return False
        if p_str.endswith("bare.git"):
            return True
        return False # Default
        
    from get_a_grip.tools.git.find_git_repo_dir import print_git_repos
    with patch('get_a_grip.tools.git.find_git_repo_dir.is_bare_repo', side_effect=bare_side_effect):
        data = find_git_repos(count=10)
        print_git_repos(data)
        
    captured = capsys.readouterr()
    
    # Check outputs
    # Non-Bare
    assert f"[REPO] {str(nb_git)}" in captured.out
    assert "Status: Non-Bare (Standard)" in captured.out
    
    # Bare
    assert f"[REPO] {str(bare_git)}" in captured.out
    assert "Status: BARE" in captured.out
    
    # File
    assert f"[REPO] {str(wt_git)}" in captured.out
    assert "Type: Git File (.git)" in captured.out
    assert "Target Status: Non-Bare" in captured.out
