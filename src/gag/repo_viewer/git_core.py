"""
git_core.py — Pure Git logic layer for gag-repo-viewer.

No tkinter dependency. All public methods return plain Python data structures
(lists of dicts, strings, booleans). The GUI layer (detect_gui.py) calls
these methods in background threads and then updates the UI via root.after().
"""

import subprocess
import os
import re
import platform


class GitRepository:
    """
    Encapsulates all Git command execution for a given working directory.
    
    Attributes:
        cwd: The current working directory.
        repo_root: The root of the git repository, or "Not a Git Repository".
    """

    def __init__(self, cwd: str):
        self.cwd = cwd
        self.repo_root = self.get_git_root()

    # ------------------------------------------------------------------
    # Low-level helpers
    # ------------------------------------------------------------------

    def _get_subprocess_kwargs(self) -> dict:
        kwargs = {"text": True, "encoding": "utf-8", "errors": "replace"}
        if os.name == "nt":
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            kwargs["startupinfo"] = si
        return kwargs

    def git_cmd(self, args: list) -> str:
        """Run a git command and return stdout, or '' on failure."""
        kwargs = self._get_subprocess_kwargs()
        try:
            return subprocess.run(
                ["git"] + args,
                capture_output=True,
                check=True,
                cwd=self.cwd,
                **kwargs,
            ).stdout.strip()
        except Exception:
            return ""

    def git_call(self, args: list) -> bool:
        """Run a git command and return True if it exits successfully."""
        kwargs = self._get_subprocess_kwargs()
        try:
            return (
                subprocess.run(
                    ["git"] + args,
                    capture_output=True,
                    check=True,
                    cwd=self.cwd,
                    **kwargs,
                ).returncode
                == 0
            )
        except Exception:
            return False

    def get_git_root(self) -> str:
        """Return the absolute path to the repo root, or a sentinel string."""
        kwargs = self._get_subprocess_kwargs()
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                capture_output=True,
                check=True,
                cwd=self.cwd,
                **kwargs,
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return "Not a Git Repository"

    # ------------------------------------------------------------------
    # Data-fetching methods (called from background threads in the GUI)
    # ------------------------------------------------------------------

    def fetch_branches(self) -> tuple:
        """
        Fetch branch relationship data relative to the current HEAD.

        Returns:
            (results, current_name, is_dirty)
            results: list of {"values": tuple, "tags": tuple}
        """
        if self.repo_root == "Not a Git Repository":
            return [], "Unknown", False

        is_dirty = bool(self.git_cmd(["status", "--porcelain"]))
        current = self.git_cmd(["branch", "--show-current"])
        if not current:
            current = self.git_cmd(["rev-parse", "--short", "HEAD"]) or "Unknown"

        raw_refs = self.git_cmd(["for-each-ref", "--format=%(refname:short)|%(objectname)"])
        reflog_raw = self.git_cmd(["log", "-g", "--all", "--format=%H %gd %s"])

        named_hashes: dict = {}
        if raw_refs:
            for line in raw_refs.split("\n"):
                if not line.strip():
                    continue
                b_name, b_hash = line.split("|")
                named_hashes.setdefault(b_hash, []).append(b_name)

        current_hash = self.git_cmd(["rev-parse", "HEAD"])

        rel_cache: dict = {}

        def get_relationship(c1, c2):
            if not c1 or not c2:
                return "Independent"
            if c1 == c2:
                return "Tip (Identical)"
            if (c1, c2) in rel_cache:
                return rel_cache[(c1, c2)]
            is_ancestor = self.git_call(["merge-base", "--is-ancestor", c2, c1])
            if is_ancestor:
                res = "Ancestor"
            else:
                is_tip_ahead = self.git_call(["merge-base", "--is-ancestor", c1, c2])
                if is_tip_ahead:
                    res = "Tip (Ahead)"
                else:
                    base = self.git_cmd(["merge-base", c1, c2])
                    res = "Diverged" if base else "Independent"
            rel_cache[(c1, c2)] = res
            return res

        results = []
        seen_hashes: set = set()

        if raw_refs:
            for line in raw_refs.split("\n"):
                if not line.strip():
                    continue
                b_name, b_hash = line.split("|")
                b_type = "Remote" if "/" in b_name else "Local"
                if b_name == current:
                    rel = "Current"
                    tags = ("current",)
                else:
                    rel = get_relationship(current_hash, b_hash)
                    if rel == "Tip (Identical)":
                        tags = ("tip",)
                    elif rel == "Ancestor":
                        tags = ("ancestor",)
                    else:
                        tags = ("independent",)
                msg = self.git_cmd(["log", "-1", "--format=%s", b_name])
                results.append({"values": (b_name, b_type, "Shared", rel, msg), "tags": tags})
                seen_hashes.add(b_hash)

        if reflog_raw:
            for line in reflog_raw.split("\n"):
                if not line.strip():
                    continue
                parts = line.split(" ", 2)
                if len(parts) < 2:
                    continue
                r_hash, r_selector = parts[0], parts[1]
                r_msg = parts[2] if len(parts) > 2 else ""
                if r_hash in seen_hashes:
                    continue
                rel = get_relationship(current_hash, r_hash)
                tags = ("reflog",)
                if rel == "Tip (Identical)":
                    tags += ("tip",)
                elif rel == "Ancestor":
                    tags += ("ancestor",)
                else:
                    tags += ("independent",)
                results.append({"values": (r_selector, "Reflog", "Shared", rel, r_msg), "tags": tags})
                seen_hashes.add(r_hash)

        return results, current, is_dirty

    def fetch_status(self) -> str:
        """Return the output of `git status`."""
        return self.git_cmd(["status"])

    def fetch_remote_tracking(self) -> list:
        """
        Fetch remote tracking branch data.

        Returns:
            list of {"values": tuple, "tags": tuple}
        """
        results = []
        bv_raw = self.git_cmd(["branch", "-vv", "--color=never"])
        tracked: set = set()
        if bv_raw:
            for line in bv_raw.split("\n"):
                if not line.strip():
                    continue
                match = re.match(r"[* ]\s+(\S+)\s+\w+\s+(?:\[([^\]]+)\]\s+)?(.*)", line)
                if match:
                    b_name, track_raw, msg = match.groups()
                    status, up = "No Tracking", ""
                    tags = ()
                    if track_raw:
                        if ":" in track_raw:
                            up, status = map(str.strip, track_raw.split(":", 1))
                        else:
                            up, status = track_raw, "Synced"
                        tracked.add(up)
                        if "gone" in status:
                            tags = ("gone",)
                        elif "ahead" in status:
                            tags = ("ahead",)
                        elif "behind" in status:
                            tags = ("behind",)
                    results.append({"values": (b_name, up, status, msg), "tags": tags})

        br_raw = self.git_cmd(["branch", "-r", "--color=never"])
        if br_raw:
            for line in br_raw.split("\n"):
                line = line.strip()
                if not line or " -> " in line:
                    continue
                if line not in tracked:
                    msg = self.git_cmd(["log", "-1", "--format=%s", line]) or ""
                    results.append({"values": (f"({line})", line, "Remote Only", msg), "tags": ("remote_only",)})

        return results

    def fetch_remotes_list(self) -> list:
        """
        Return registered remotes.

        Returns:
            list of (name, url, type) tuples
        """
        results = []
        rm_raw = self.git_cmd(["remote", "-v"])
        if rm_raw:
            for line in rm_raw.split("\n"):
                parts = line.strip().split()
                if len(parts) >= 2:
                    rtype = parts[2].strip("()") if len(parts) > 2 else ""
                    results.append((parts[0], parts[1], rtype))
        return results

    def rename_remote(self, old_name: str, new_name: str) -> bool:
        """Rename a git remote. Returns True on success."""
        kwargs = self._get_subprocess_kwargs()
        kwargs["stdout"] = subprocess.PIPE
        try:
            subprocess.run(
                ["git", "remote", "rename", old_name, new_name],
                check=True,
                cwd=self.cwd,
                **kwargs,
            )
            return True
        except subprocess.CalledProcessError:
            return False

    def fetch_submodules(self) -> list:
        """
        Fetch submodule status data.

        Returns:
            list of {"values": tuple, "tags": tuple}
        """
        if self.repo_root == "Not a Git Repository":
            return []

        status_raw = self.git_cmd(["submodule", "status", "--recursive"])
        if not status_raw:
            return []

        results = []
        for line in status_raw.split("\n"):
            line = line.strip()
            if not line:
                continue
            match = re.match(r"([ +\-])([0-9a-f]+)\s+([^\s]+)(?:\s+\((.+)\))?", line)
            if not match:
                continue
            prefix, actual_hash, path, _ = match.groups()
            name = path

            status = "Clean"
            tags = ("clean",)
            if prefix == "+":
                status = "Modified"
                tags = ("dirty",)
            elif prefix == "-":
                status = "Not Init"
                tags = ("detached",)

            recorded_hash_parts = self.git_cmd(["ls-tree", "HEAD", path]).split()
            recorded_hash = recorded_hash_parts[2] if len(recorded_hash_parts) > 2 else "Unknown"

            sm_abs_path = os.path.join(self.repo_root, path)
            sm_branch = "Unknown"
            upstream_status = "Unknown"
            upstream_tags = ()

            if os.path.isdir(sm_abs_path):
                def sm_git(args):
                    kwargs = self._get_subprocess_kwargs()
                    try:
                        return subprocess.run(
                            ["git"] + args,
                            capture_output=True,
                            check=True,
                            cwd=sm_abs_path,
                            **kwargs,
                        ).stdout.strip()
                    except Exception:
                        return ""

                sm_branch = sm_git(["branch", "--show-current"]) or "Detached HEAD"
                if sm_branch == "Detached HEAD":
                    sm_branch = f"({sm_git(['rev-parse', '--short', 'HEAD'])})"
                    upstream_tags = ("detached",)

                tracking = sm_git(["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"])
                if tracking:
                    behind_commits = sm_git(["log", "HEAD..@{u}", "--oneline"])
                    if behind_commits:
                        count = len(behind_commits.split("\n"))
                        upstream_status = f"Behind by {count}"
                        upstream_tags += ("behind",)
                    else:
                        upstream_status = "Up-to-date"
                        upstream_tags += ("clean",)
                else:
                    upstream_status = "No Tracking"

            results.append({
                "values": (path, name, sm_branch, status, upstream_status, recorded_hash[:8], actual_hash[:8]),
                "tags": tags + upstream_tags,
            })

        return results

    def open_terminal(self, cwd: str):
        """Open a terminal window at the given directory."""
        try:
            if os.name == "nt":
                try:
                    subprocess.Popen(["wt.exe", "-d", cwd])
                except FileNotFoundError:
                    subprocess.Popen(["powershell.exe"], cwd=cwd, creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:
                if platform.system() == "Darwin":
                    subprocess.Popen(["open", "-a", "Terminal", cwd])
                else:
                    subprocess.Popen(["x-terminal-emulator"], cwd=cwd)
        except Exception as e:
            raise RuntimeError(f"Failed to open terminal: {e}") from e
