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

# Test pygit2 backend info extraction
def test_get_git_info_pygit2_success():
    with patch('get_a_grip.tools.git.find_github_dir.pygit2') as mock_pygit2:
        mock_repo = MagicMock()
        mock_repo.is_bare = False
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

# Test dulwich backend info extraction
def test_get_git_info_dulwich_success():
    with patch('get_a_grip.tools.git.find_github_dir.dulwich') as mock_dulwich:
        mock_repo = MagicMock()
        # Mock HEAD read
        mock_repo.refs.read_ref.return_value = b'ref: refs/heads/master'
        mock_dulwich.repo.Repo.return_value = mock_repo
        
        result = get_git_info_dulwich("/path/to/repo")
        assert "master" in result 
        
# Test dispatch logic
def test_get_git_info_dispatch():
    with patch('get_a_grip.tools.git.find_github_dir.get_git_info_gitpython') as mock_gp:
        get_git_info("/p", "gitpython")
        mock_gp.assert_called_once()
        
    with patch('get_a_grip.tools.git.find_github_dir.get_git_info_pygit2') as mock_pg:
        get_git_info("/p", "pygit2")
        mock_pg.assert_called_once()

# Test the main flow (Integration-ish)
@patch('get_a_grip.tools.git.find_github_dir.scan_by_ipc')
def test_find_github_dir_integration(mock_scan, capsys):
    # Mock Everything search returning one directory
    mock_scan.return_value = {"dirs": [{"Filename": "/mock/GitHub"}]}
    
    # Mock os.scandir to return entries inside that directory
    mock_entry = MagicMock()
    mock_entry.is_dir.return_value = True
    mock_entry.path = "/mock/GitHub/my-project"
    mock_entry.name = "my-project"
    
    # Context manager mock for scandir
    mock_scandir_ctx = MagicMock()
    mock_scandir_ctx.__enter__.return_value = [mock_entry]
    mock_scandir_ctx.__exit__.return_value = None
    
    with patch('os.scandir', return_value=mock_scandir_ctx):
        # Mock GitPython backend call to return info string
        with patch('get_a_grip.tools.git.find_github_dir.get_git_info_gitpython', return_value=" <GitPython:main (clean)>"):
             # Also ensure git is mocked as present
             with patch('get_a_grip.tools.git.find_github_dir.git'):
                find_github_dir(count=1, backend="gitpython")
    
    captured = capsys.readouterr()
    assert "Searching for potential GitHub directories" in captured.out
    assert "/mock/GitHub/my-project <GitPython:main (clean)>" in captured.out

def test_find_github_dir_no_results(capsys):
    with patch('get_a_grip.tools.git.find_github_dir.scan_by_ipc', return_value={"dirs": []}):
        # Mock git present
         with patch('get_a_grip.tools.git.find_github_dir.git'):
             find_github_dir(backend="gitpython")
             
    captured = capsys.readouterr()
    assert "No folders named 'GitHub' found" in captured.out
