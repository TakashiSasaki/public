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
    # Mock is_bare_repo return using patch
    with patch('get_a_grip.tools.git.find_git_repo_dir.is_bare_repo', return_value=False):
        info = check_path_info(str(git_dir))
        # Expected: worktree_dir is parent of .git
        assert info["worktree_dir"] == str(tmp_path)
        assert info["repo_dir"] == str(git_dir)
        assert info["is_bare"] is False

def test_check_path_info_dir_bare(tmp_path):
    # Setup bare repo dir (name usually ends in .git)
    bare_dir = tmp_path / "repo.git"
    bare_dir.mkdir()
    with patch('get_a_grip.tools.git.find_git_repo_dir.is_bare_repo', return_value=True):
        info = check_path_info(str(bare_dir))
        # For bare repo, usually considered its own worktree/root context in this simple logic
        assert info["repo_dir"] == str(bare_dir)
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
        assert info["worktree_dir"] == str(wt_root)
        # Check resolved absolute path
        assert os.path.normcase(info["repo_dir"]) == os.path.normcase(str(real_git))
        assert info["is_bare"] is False

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
    assert f"Worktree: {str(nb_root)}" in captured.out
    assert f"Git Dir : {str(nb_git)}" in captured.out
    assert "Status  : Standard" in captured.out
    
    # Bare
    # For directory scan, worktree is set to parent, likely matches bare_git parent or bare_git depending on logic
    # In check_path_info: worktree_dir = os.path.dirname(path)
    assert f"Worktree: {str(tmp_path)}" in captured.out
    assert f"Git Dir : {str(bare_git)}" in captured.out
    assert "Status  : BARE" in captured.out
    
    # File
    assert f"Worktree: {str(wt_root)}" in captured.out
    # git_file is path to .git file, but repo_dir resolves to target
    # print_git_repos uses repo_dir
    assert f"Git Dir : {str(nb_git)}" in captured.out
