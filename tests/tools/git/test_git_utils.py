import os
import time
from unittest.mock import patch

from get_a_grip.core.git.utils import (
    IGNORED_GIT_ENV_VARS,
    get_git_info_with_timeout,
    get_head_content,
    get_refs_and_remotes,
    is_bare_repo,
    sanitized_git_environment,
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
    with patch("get_a_grip.core.git.utils.git", None):
        with patch("get_a_grip.core.git.utils.pygit2", None):
            with patch("get_a_grip.core.git.utils.dulwich", None):
                refs, remotes = get_refs_and_remotes("C:/repo")
    assert refs == []
    assert remotes == []

def test_sanitized_git_environment_removes_and_restores(monkeypatch):
    key = "GIT_DIR"
    monkeypatch.setenv(key, "C:/poisoned")
    with sanitized_git_environment():
        assert key not in os.environ
    assert os.environ.get(key) == "C:/poisoned"

def test_get_refs_and_remotes_ignores_git_env(monkeypatch):
    monkeypatch.setenv("GIT_DIR", "C:/poisoned")

    class FakeRemote:
        name = "origin"

        @property
        def urls(self):
            return iter(["https://example.invalid/repo.git"])

    class FakeRepo:
        references = ["refs/heads/main"]
        remotes = [FakeRemote()]

    class FakeGitModule:
        @staticmethod
        def Repo(path, search_parent_directories=False):
            assert "GIT_DIR" not in os.environ
            return FakeRepo()

    with patch("get_a_grip.core.git.utils.git", FakeGitModule):
        with patch("get_a_grip.core.git.utils.pygit2", None):
            with patch("get_a_grip.core.git.utils.dulwich", None):
                refs, remotes = get_refs_and_remotes("C:/repo")

    assert refs == ["refs/heads/main"]
    assert remotes == ["origin: https://example.invalid/repo.git"]
    assert os.environ.get("GIT_DIR") == "C:/poisoned"

def test_ignored_git_env_vars_contains_critical_keys():
    assert "GIT_DIR" in IGNORED_GIT_ENV_VARS
    assert "GIT_WORK_TREE" in IGNORED_GIT_ENV_VARS
    assert "GIT_INDEX_FILE" in IGNORED_GIT_ENV_VARS


def test_is_bare_repo_uses_config_fallback(tmp_path):
    repo_git_dir = tmp_path / "repo.git"
    repo_git_dir.mkdir()
    (repo_git_dir / "config").write_text("[core]\n\tbare = true\n", encoding="utf-8")
    with patch("get_a_grip.core.git.utils.git", None):
        with patch("get_a_grip.core.git.utils.pygit2", None):
            with patch("get_a_grip.core.git.utils.dulwich", None):
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

