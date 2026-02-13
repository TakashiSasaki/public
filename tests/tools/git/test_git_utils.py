import os
import time
from unittest.mock import patch

from get_a_grip.tools.git.utils import (
    get_git_info_with_timeout,
    get_head_content,
    get_refs_and_remotes,
    is_bare_repo,
)


def test_get_head_content_from_git_dir(tmp_path):
    repo = tmp_path / "repo"
    (repo / ".git").mkdir(parents=True)
    (repo / ".git" / "HEAD").write_text("ref: refs/heads/main", encoding="utf-8")
    assert get_head_content(str(repo)) == "ref: refs/heads/main"


def test_get_head_content_not_found(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    assert get_head_content(str(repo)) == "[Not Found]"


def test_get_head_content_from_gitfile_linked_head(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    real_git = tmp_path / "real.git"
    real_git.mkdir()
    (real_git / "HEAD").write_text("ref: refs/heads/linked", encoding="utf-8")
    rel = os.path.relpath(real_git, repo)
    (repo / ".git").write_text(f"gitdir: {rel}", encoding="utf-8")
    assert get_head_content(str(repo)) == "ref: refs/heads/linked"


def test_get_refs_and_remotes_returns_empty_when_no_backends():
    with patch("get_a_grip.tools.git.utils.git", None):
        with patch("get_a_grip.tools.git.utils.pygit2", None):
            with patch("get_a_grip.tools.git.utils.dulwich", None):
                refs, remotes = get_refs_and_remotes("C:/repo")
    assert refs == []
    assert remotes == []


def test_is_bare_repo_uses_config_fallback(tmp_path):
    repo_git_dir = tmp_path / "repo.git"
    repo_git_dir.mkdir()
    (repo_git_dir / "config").write_text("[core]\n\tbare = true\n", encoding="utf-8")
    with patch("get_a_grip.tools.git.utils.git", None):
        with patch("get_a_grip.tools.git.utils.pygit2", None):
            with patch("get_a_grip.tools.git.utils.dulwich", None):
                assert is_bare_repo(str(repo_git_dir)) is True


def test_get_git_info_with_timeout_timeout():
    def sleeper(_path):
        time.sleep(0.05)
        return {"info": "ok", "is_clean": True, "has_untracked": False}

    result = get_git_info_with_timeout(sleeper, "C:/repo", timeout=0.001)
    assert result["info"] == "[Timeout]"
    assert result["is_clean"] is None


def test_get_git_info_with_timeout_exception():
    def boom(_path):
        raise RuntimeError("x")

    result = get_git_info_with_timeout(boom, "C:/repo", timeout=0.001)
    assert result["info"].startswith("Error:")
    assert result["has_untracked"] is None

