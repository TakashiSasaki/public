import os
from collections import Counter
from unittest.mock import patch

from get_a_grip.tools.git.find_git_repo import (
    check_path_info,
    find_git_repos,
    print_git_repos
)

# check_path_info integration with temp fs
def test_check_path_info_dir_non_bare(tmp_path):
    # Setup standard .git dir
    git_dir = tmp_path / ".git"
    git_dir.mkdir()
    
    # Mock is_bare_repo return using patch on the module where check_path_info is defined
    with patch('get_a_grip.tools.git.find_git_repo.is_bare_repo', return_value=False):
        # We also need to ensure refs/remotes/head don't fail or return predictable values
        with patch('get_a_grip.tools.git.find_git_repo.get_refs_and_remotes', return_value=([], [])):
             # And ensure HEAD file exists or get_head_content logic is handled
             # check_path_info reads HEAD manually if not found? 
             # No, check_path_info calls get_head_content but mostly relies on it?
             # Actually check_path_info has its own logic for HEAD reading inside the function now?
             # Let's check the code: yes, it tries to read HEAD manually if is_bare_repo succeeds
             (git_dir / "HEAD").write_text("ref: refs/heads/main", encoding="utf-8")
             
             info = check_path_info(str(git_dir))
             
             # Expected: git_repo_dir is the .git dir itself
             assert info["git_repo_dir"] == str(git_dir)
             assert info["is_bare"] is False
             assert info["head"] == "ref: refs/heads/main"
             assert info["is_detached"] is False

def test_check_path_info_dir_bare(tmp_path):
    # Setup bare repo dir (name usually ends in .git)
    bare_dir = tmp_path / "repo.git"
    bare_dir.mkdir()
    
    with patch('get_a_grip.tools.git.find_git_repo.is_bare_repo', return_value=True):
        with patch('get_a_grip.tools.git.find_git_repo.get_refs_and_remotes', return_value=([], [])):
            (bare_dir / "HEAD").write_text("ref: refs/heads/main", encoding="utf-8")
            
            info = check_path_info(str(bare_dir))
             
            assert info["git_repo_dir"] == str(bare_dir)
            assert info["is_bare"] is True
            assert info["is_detached"] is False

def test_check_path_info_file(tmp_path):
    # Setup .git file
    wt_root = tmp_path / "wt"
    wt_root.mkdir()
    git_file = wt_root / ".git"
    # Point to a fake existing dir
    real_git = tmp_path / "real.git"
    real_git.mkdir()
    # Create HEAD in real git
    (real_git / "HEAD").write_text("ref: refs/heads/main", encoding="utf-8")
    
    rel_path = os.path.relpath(real_git, wt_root)
    git_file.write_text(f"gitdir: {rel_path}", encoding="utf-8")
    
    with patch('get_a_grip.tools.git.find_git_repo.is_bare_repo', return_value=False):
        with patch('get_a_grip.tools.git.find_git_repo.get_refs_and_remotes', return_value=([], [])):
            info = check_path_info(str(git_file))
            
            # Check resolved absolute path
            assert os.path.normcase(info["git_repo_dir"]) == os.path.normcase(str(real_git))
            assert info["is_bare"] is False
            assert info["is_detached"] is False

def test_check_path_info_returns_none_when_head_missing(tmp_path):
    git_dir = tmp_path / ".git"
    git_dir.mkdir()

    with patch('get_a_grip.tools.git.find_git_repo.is_bare_repo', return_value=False):
        with patch('get_a_grip.tools.git.find_git_repo.get_refs_and_remotes', return_value=([], [])):
            info = check_path_info(str(git_dir))

    assert info is None

def test_check_path_info_returns_none_when_head_empty(tmp_path):
    git_dir = tmp_path / ".git"
    git_dir.mkdir()
    (git_dir / "HEAD").write_text("", encoding="utf-8")

    with patch('get_a_grip.tools.git.find_git_repo.is_bare_repo', return_value=False):
        with patch('get_a_grip.tools.git.find_git_repo.get_refs_and_remotes', return_value=([], [])):
            info = check_path_info(str(git_dir))

    assert info is None

def test_check_path_info_returns_none_on_head_read_error(tmp_path):
    git_dir = tmp_path / ".git"
    git_dir.mkdir()
    (git_dir / "HEAD").write_text("ref: refs/heads/main", encoding="utf-8")

    original_open = open

    def open_side_effect(path, *args, **kwargs):
        if os.path.normcase(str(path)) == os.path.normcase(str(git_dir / "HEAD")):
            raise OSError("simulated read error")
        return original_open(path, *args, **kwargs)

    with patch('get_a_grip.tools.git.find_git_repo.is_bare_repo', return_value=False):
        with patch('get_a_grip.tools.git.find_git_repo.get_refs_and_remotes', return_value=([], [])):
            with patch('builtins.open', side_effect=open_side_effect):
                info = check_path_info(str(git_dir))

    assert info is None

def test_check_path_info_returns_none_for_invalid_gitfile_prefix(tmp_path):
    wt_root = tmp_path / "wt"
    wt_root.mkdir()
    git_file = wt_root / ".git"
    git_file.write_text("not-a-gitdir-file", encoding="utf-8")

    info = check_path_info(str(git_file))
    assert info is None

def test_check_path_info_returns_none_for_missing_gitdir_target(tmp_path):
    wt_root = tmp_path / "wt"
    wt_root.mkdir()
    git_file = wt_root / ".git"
    git_file.write_text("gitdir: ../missing.git", encoding="utf-8")

    info = check_path_info(str(git_file))
    assert info is None

@patch('get_a_grip.tools.git.find_git_repo.scan_by_ipc')
def test_find_git_repos_integration(mock_scan, tmp_path, capsys):
    # Setup
    # 1. Non-Bare (.git dir)
    nb_root = tmp_path / "nb_root"
    nb_root.mkdir()
    nb_git = nb_root / ".git"
    nb_git.mkdir()
    (nb_git / "HEAD").write_text("ref: refs/heads/main", encoding="utf-8")
    
    # 2. Bare (bare.git dir)
    bare_git = tmp_path / "bare.git"
    bare_git.mkdir()
    (bare_git / "HEAD").write_text("ref: refs/heads/main", encoding="utf-8")
    
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
    
    # Mock Utils
    def bare_side_effect(path):
        p_str = str(path).replace("\\", "/")
        if p_str.endswith(".git") and "nb_root" in p_str:
            return False
        if p_str.endswith("bare.git"):
            return True
        return False
        
    with patch('get_a_grip.tools.git.find_git_repo.is_bare_repo', side_effect=bare_side_effect):
        with patch('get_a_grip.tools.git.find_git_repo.get_refs_and_remotes', return_value=([], [])):
            data = find_git_repos(count=10)
            print_git_repos(data)
        
    captured = capsys.readouterr()
    
    # Check outputs
    # Non-Bare repo dir
    assert f"Dir : {str(nb_git)}" in captured.out
    assert "Status  : Standard" in captured.out
    
    # Bare repo dir
    assert f"Dir : {str(bare_git)}" in captured.out
    assert "Status  : BARE" in captured.out

    # Validate returned data directly, not only print output
    assert data["count"] == 3
    repo_dirs = [os.path.normcase(repo["git_repo_dir"]) for repo in data["repos"]]
    counts = Counter(repo_dirs)
    assert counts[os.path.normcase(str(nb_git))] == 2
    assert counts[os.path.normcase(str(bare_git))] == 1

def test_find_git_repos_handles_ipc_failures():
    with patch('get_a_grip.tools.git.find_git_repo.scan_by_ipc', side_effect=RuntimeError("ipc-fail")):
        data = find_git_repos(count=10)

    assert data["count"] == 0
    assert data["repos"] == []

def test_print_git_repos_prints_detached_remotes_and_refs(capsys):
    data = {
        "repos": [
            {
                "git_repo_dir": "C:/repo/.git",
                "is_bare": False,
                "is_detached": True,
                "head": "deadbeef1234",
                "refs": ["refs/heads/main"],
                "remotes": ["origin: https://example.invalid/repo.git"],
            }
        ],
        "count": 1,
    }

    print_git_repos(data)
    captured = capsys.readouterr().out
    assert "State   : DETACHED" in captured
    assert "Remotes : origin: https://example.invalid/repo.git" in captured
    assert "Refs    : 1 refs" in captured
