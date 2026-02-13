import os
from unittest.mock import patch

from get_a_grip.tools.git.find_git_worktree import (
    find_git_worktrees,
    get_status_with_timeout,
    get_worktree_status_dulwich,
    get_worktree_status_gitpython,
    get_worktree_status_pygit2,
    print_git_worktrees,
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

@patch('get_a_grip.tools.git.find_git_worktree.scan_by_ipc')
def test_find_git_worktrees_conflicting_backend_votes(mock_scan, tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / ".git").mkdir()
    (repo / ".git" / "HEAD").write_text("ref: refs/heads/main", encoding="utf-8")

    def scan_side_effect(query, count):
        if "folder:" in query and "!folder:" not in query:
            return {"dirs": [{"Filename": str(repo / ".git")}], "files": []}
        return {"files": [], "dirs": []}

    mock_scan.side_effect = scan_side_effect

    with patch('get_a_grip.tools.git.find_git_worktree.get_worktree_status_gitpython', return_value={"is_clean": True, "has_untracked": False}):
        with patch('get_a_grip.tools.git.find_git_worktree.get_worktree_status_pygit2', return_value={"is_clean": False, "has_untracked": True}):
            with patch('get_a_grip.tools.git.find_git_worktree.get_worktree_status_dulwich', return_value=None):
                data = find_git_worktrees(count=10, timeout=0)

    assert data["count"] == 1
    wt = data["worktrees"][0]
    # Conflicting is_clean votes must resolve to False (dirty-safe).
    assert wt["is_clean"] is False
    # Conflicting has_untracked votes resolve via any().
    assert wt["has_untracked"] is True

@patch('get_a_grip.tools.git.find_git_worktree.scan_by_ipc')
def test_find_git_worktrees_skips_candidates_with_no_valid_backend(mock_scan, tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / ".git").mkdir()
    (repo / ".git" / "HEAD").write_text("ref: refs/heads/main", encoding="utf-8")

    def scan_side_effect(query, count):
        if "folder:" in query and "!folder:" not in query:
            return {"dirs": [{"Filename": str(repo / ".git")}], "files": []}
        return {"files": [], "dirs": []}

    mock_scan.side_effect = scan_side_effect

    with patch('get_a_grip.tools.git.find_git_worktree.get_worktree_status_gitpython', return_value=None):
        with patch('get_a_grip.tools.git.find_git_worktree.get_worktree_status_pygit2', return_value=None):
            with patch('get_a_grip.tools.git.find_git_worktree.get_worktree_status_dulwich', return_value=None):
                data = find_git_worktrees(count=10, timeout=0)

    assert data["count"] == 0
    assert data["worktrees"] == []

def test_get_worktree_status_gitpython_missing_backend():
    with patch('get_a_grip.tools.git.find_git_worktree.git', None):
        assert get_worktree_status_gitpython("C:/repo") is None

def test_get_worktree_status_gitpython_success():
    with patch('get_a_grip.tools.git.find_git_worktree.git') as mock_git:
        mock_repo = mock_git.Repo.return_value
        mock_repo.is_dirty.return_value = False
        mock_repo.git.ls_files.return_value = "tmp.txt\n"
        result = get_worktree_status_gitpython("C:/repo")
    assert result == {"is_clean": True, "has_untracked": True, "valid": True}

def test_get_worktree_status_gitpython_ignores_git_env(monkeypatch):
    monkeypatch.setenv("GIT_DIR", "C:/poisoned")

    class FakeRepo:
        def __init__(self):
            self.is_dirty = lambda untracked_files=False: False
            self.git = type("GitCmd", (), {"ls_files": staticmethod(lambda *args: "")})()

    class FakeGit:
        @staticmethod
        def Repo(path, search_parent_directories=False):
            assert "GIT_DIR" not in os.environ
            return FakeRepo()

    with patch("get_a_grip.tools.git.find_git_worktree.git", FakeGit):
        result = get_worktree_status_gitpython("C:/repo")
    assert result["is_clean"] is True
    assert os.environ.get("GIT_DIR") == "C:/poisoned"

def test_get_worktree_status_pygit2_bare():
    with patch('get_a_grip.tools.git.find_git_worktree.pygit2') as mock_pygit2:
        mock_repo = mock_pygit2.Repository.return_value
        mock_repo.is_bare = True
        result = get_worktree_status_pygit2("C:/repo")
    assert result == {"is_clean": True, "has_untracked": False, "valid": True}

def test_get_worktree_status_pygit2_ignores_git_env(monkeypatch):
    monkeypatch.setenv("GIT_WORK_TREE", "C:/poisoned")

    class FakeRepo:
        is_bare = True

    class FakePygit2:
        GIT_STATUS_WT_NEW = 0x80

        @staticmethod
        def Repository(path):
            assert "GIT_WORK_TREE" not in os.environ
            return FakeRepo()

    with patch("get_a_grip.tools.git.find_git_worktree.pygit2", FakePygit2):
        result = get_worktree_status_pygit2("C:/repo")
    assert result["is_clean"] is True
    assert os.environ.get("GIT_WORK_TREE") == "C:/poisoned"

def test_get_worktree_status_pygit2_dirty_and_untracked():
    with patch('get_a_grip.tools.git.find_git_worktree.pygit2') as mock_pygit2:
        mock_repo = mock_pygit2.Repository.return_value
        mock_repo.is_bare = False
        mock_repo.status.return_value = {
            "new.txt": mock_pygit2.GIT_STATUS_WT_NEW,
            "tracked.txt": 0x02,
        }
        result = get_worktree_status_pygit2("C:/repo")
    assert result == {"is_clean": False, "has_untracked": True, "valid": True}

def test_get_worktree_status_dulwich_status_error():
    with patch('get_a_grip.tools.git.find_git_worktree.dulwich') as mock_dulwich:
        mock_dulwich.repo.Repo.return_value = object()
        mock_dulwich.porcelain.status.side_effect = RuntimeError("status fail")
        assert get_worktree_status_dulwich("C:/repo") is None

def test_get_worktree_status_dulwich_ignores_git_env(monkeypatch):
    monkeypatch.setenv("GIT_INDEX_FILE", "C:/poisoned")

    class FakeRepo:
        pass

    class FakePorcelain:
        @staticmethod
        def status(repo):
            return ({"add": []}, [], [])

    class FakeDulwich:
        class repo:
            @staticmethod
            def Repo(path):
                assert "GIT_INDEX_FILE" not in os.environ
                return FakeRepo()

        porcelain = FakePorcelain

    with patch("get_a_grip.tools.git.find_git_worktree.dulwich", FakeDulwich):
        result = get_worktree_status_dulwich("C:/repo")
    assert result["is_clean"] is True
    assert os.environ.get("GIT_INDEX_FILE") == "C:/poisoned"

def test_get_status_with_timeout_returns_none_on_timeout():
    def sleeper(_):
        import time
        time.sleep(0.05)
        return {"is_clean": True, "has_untracked": False}

    result = get_status_with_timeout(sleeper, "C:/repo", 0.001)
    assert result is None

def test_print_git_worktrees_timeout_and_detached(capsys):
    data = {
        "worktrees": [
            {
                "git_worktree_dir": "C:/repo",
                "is_clean": True,
                "has_untracked": False,
                "git_repo_info": {
                    "git_repo_dir": "C:/repo/.git",
                    "is_bare": False,
                    "is_detached": True,
                    "head": "deadbeef",
                    "refs": ["refs/heads/main"],
                    "remotes": ["origin: https://example.invalid/repo.git"],
                },
            }
        ],
        "count": 1,
    }
    print_git_worktrees(data, timeout=1.0)
    captured = capsys.readouterr().out
    assert "Start Timeout: 1.0 seconds" in captured
    assert "HEAD      : deadbeef (DETACHED)" in captured
    assert "Remotes   : origin: https://example.invalid/repo.git" in captured
