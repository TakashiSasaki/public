import pytest
from unittest.mock import MagicMock, patch, mock_open

# Import functions to test
from get_a_grip.tools.git.find_github_dir import (
    get_git_info_gitpython, 
    get_git_info_pygit2,
    get_git_info_dulwich,
    get_git_info,
    find_github_dir
)

# Test GitPython backend info extraction
def test_get_git_info_gitpython_success():
    with patch('get_a_grip.tools.git.find_github_dir.git') as mock_git:
        mock_repo = MagicMock()
        mock_repo.active_branch.name = "main"
        mock_repo.is_dirty.return_value = False
        mock_repo.head.is_detached = False
        mock_git.Repo.return_value = mock_repo
        
        result = get_git_info_gitpython("/path/to/repo")
        assert "main" in result
        assert "clean" in result
        mock_git.Repo.assert_called_with("/path/to/repo", search_parent_directories=False)

def test_get_git_info_gitpython_detached():
    with patch('get_a_grip.tools.git.find_github_dir.git') as mock_git:
        mock_repo = MagicMock()
        mock_repo.head.is_detached = True
        mock_repo.is_dirty.return_value = True
        mock_git.Repo.return_value = mock_repo
        
        result = get_git_info_gitpython("/path/to/repo")
        assert "DETACHED" in result
        assert "dirty" in result

def test_get_git_info_gitpython_missing():
    with patch('get_a_grip.tools.git.find_github_dir.git', None):
        result = get_git_info_gitpython("/path/to/repo")
        assert "not installed" in result

def test_get_git_info_gitpython_invalid_repo():
    with patch('get_a_grip.tools.git.find_github_dir.git') as mock_git:
        mock_git.InvalidGitRepositoryError = RuntimeError
        mock_git.NoSuchPathError = FileNotFoundError
        mock_git.Repo.side_effect = RuntimeError("invalid")
        result = get_git_info_gitpython("/path/to/repo")
        assert result == ""

def test_get_git_info_gitpython_unexpected_error():
    class CustomError(Exception):
        pass

    with patch('get_a_grip.tools.git.find_github_dir.git') as mock_git:
        mock_git.InvalidGitRepositoryError = RuntimeError
        mock_git.NoSuchPathError = FileNotFoundError
        mock_git.Repo.side_effect = CustomError("boom")
        result = get_git_info_gitpython("/path/to/repo")
        assert "GitPython Error: CustomError" in result

# Test pygit2 backend info extraction
def test_get_git_info_pygit2_success():
    with patch('get_a_grip.tools.git.find_github_dir.pygit2') as mock_pygit2:
        mock_repo = MagicMock()
        mock_repo.is_bare = False
        mock_repo.head_is_detached = False
        mock_repo.head.shorthand = "dev"
        mock_repo.status.return_value = {} # clean
        mock_pygit2.Repository.return_value = mock_repo
        
        result = get_git_info_pygit2("/path/to/repo")
        assert "dev" in result
        assert "clean" in result

def test_get_git_info_pygit2_bare():
    with patch('get_a_grip.tools.git.find_github_dir.pygit2') as mock_pygit2:
        mock_repo = MagicMock()
        mock_repo.is_bare = True
        mock_pygit2.Repository.return_value = mock_repo
        
        result = get_git_info_pygit2("/path/to/repo")
        assert "bare" in result

def test_get_git_info_pygit2_missing():
    with patch('get_a_grip.tools.git.find_github_dir.pygit2', None):
        result = get_git_info_pygit2("/path/to/repo")
        assert "not installed" in result

def test_get_git_info_pygit2_headless():
    with patch('get_a_grip.tools.git.find_github_dir.pygit2') as mock_pygit2:
        mock_repo = MagicMock()
        mock_repo.is_bare = False
        mock_repo.head_is_detached = False
        type(mock_repo).head = property(lambda _self: (_ for _ in ()).throw(RuntimeError("no head")))
        mock_repo.status.return_value = {"a": 1}
        mock_pygit2.Repository.return_value = mock_repo
        result = get_git_info_pygit2("/path/to/repo")
        assert "HEADLESS" in result
        assert "dirty" in result

# Test dulwich backend info extraction
def test_get_git_info_dulwich_success():
    with patch('get_a_grip.tools.git.find_github_dir.dulwich') as mock_dulwich:
        mock_repo = MagicMock()
        # Mock HEAD read
        mock_repo.refs.read_ref.return_value = b'ref: refs/heads/master'
        mock_dulwich.repo.Repo.return_value = mock_repo
        
        result = get_git_info_dulwich("/path/to/repo")
        assert "master" in result 

def test_get_git_info_dulwich_missing():
    with patch('get_a_grip.tools.git.find_github_dir.dulwich', None):
        result = get_git_info_dulwich("/path/to/repo")
        assert "not installed" in result

def test_get_git_info_dulwich_headless():
    with patch('get_a_grip.tools.git.find_github_dir.dulwich') as mock_dulwich:
        mock_repo = MagicMock()
        mock_repo.refs.read_ref.side_effect = KeyError("HEAD")
        mock_dulwich.repo.Repo.return_value = mock_repo
        result = get_git_info_dulwich("/path/to/repo")
        assert "HEADLESS" in result
         
# Test dispatch logic
def test_get_git_info_dispatch():
    with patch('get_a_grip.tools.git.find_github_dir.get_git_info_gitpython') as mock_gp:
        get_git_info("/p", "gitpython")
        mock_gp.assert_called_once()
        
    with patch('get_a_grip.tools.git.find_github_dir.get_git_info_pygit2') as mock_pg:
        get_git_info("/p", "pygit2")
        mock_pg.assert_called_once()

    assert "[Unknown Backend]" in get_git_info("/p", "unknown")

# Test the main flow (Integration with Real Filesystem)
@patch('get_a_grip.tools.git.find_github_dir.scan_by_ipc')
def test_find_github_dir_real_fs(mock_scan, tmp_path, capsys):
    """
    Test find_github_dir using real directory traversal on a temporary filesystem.
    Everything IPC and Git backend check are mocked contextually.
    """
    # 1. Setup Directory Structure in tmp_path
    # tmp_path/
    #   FakeGitHub/
    #     valid-repo/   (Should be found)
    #     not-a-repo/   (Should be skipped)
    #     some-file.txt (Should be skipped)

    fake_github = tmp_path / "FakeGitHub"
    fake_github.mkdir()
    
    valid_repo = fake_github / "valid-repo"
    valid_repo.mkdir()
    
    not_a_repo = fake_github / "not-a-repo"
    not_a_repo.mkdir()
    
    some_file = fake_github / "some-file.txt"
    some_file.touch()

    # 2. Mock Everything result to point to our fake GitHub folder
    mock_scan.return_value = {
        "dirs": [{"Filename": str(fake_github)}],
        "files": []
    }
    
    # 3. Partially mock Git backend check
    # We want to verified that valid-repo is detected as Git repo, and not-a-repo is not.
    # We use side_effect to return different values based on path.
    
    from pathlib import Path
    
    def get_info_side_effect(path):
        # Normalize paths for comparison
        p = Path(path).resolve()
        v = valid_repo.resolve()
        
        if p == v:
            return " <GitPython:main (clean)>"
        return "" # Empty string means not a repo

    from get_a_grip.tools.git.find_github_dir import print_github_repos
    with patch('get_a_grip.tools.git.find_github_dir.get_git_info_gitpython', side_effect=get_info_side_effect):
        # Also ensure git is mocked as present so the check passes
        with patch('get_a_grip.tools.git.find_github_dir.git'):
            data = find_github_dir(count=1, backend="gitpython")
            print_github_repos(data)
            
    # 4. Verify Output
    captured = capsys.readouterr()
    
    # Check that valid repo is found
    # Note: Output path might have different casing on Windows, so we check loosely or normalize
    assert str(valid_repo) in captured.out
    assert "<GitPython:main (clean)>" in captured.out
    
    # Check that invalid repo is NOT found (it was scanned but get_info returned empty)
    assert str(not_a_repo) not in captured.out
    
    # Check that file is skipped (not even passed to get_info)
    assert str(some_file) not in captured.out

def test_find_github_dir_no_results(capsys):
    from get_a_grip.tools.git.find_github_dir import print_github_repos
    with patch('get_a_grip.tools.git.find_github_dir.scan_by_ipc', return_value={"dirs": []}):
        data = find_github_dir(backend="gitpython")
        print_github_repos(data)
             
    captured = capsys.readouterr()
    assert "No folders named 'GitHub' found" in captured.out

def test_find_github_dir_scan_exception():
    with patch('get_a_grip.tools.git.find_github_dir.scan_by_ipc', side_effect=RuntimeError("ipc-fail")):
        data = find_github_dir(backend="gitpython")
    assert data["roots_found"] is False
    assert data["count"] == 0

def test_print_github_repos_roots_found_but_no_repos(capsys):
    from get_a_grip.tools.git.find_github_dir import print_github_repos
    data = {"repos": [], "count": 0, "backend": "gitpython", "roots_found": True}
    print_github_repos(data)
    captured = capsys.readouterr().out
    assert "No valid Git repositories found inside 'GitHub' folders." in captured
