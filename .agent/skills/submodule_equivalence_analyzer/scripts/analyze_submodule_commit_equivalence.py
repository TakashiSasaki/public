#!/usr/bin/env python3
"""Analyze shared commit history across git submodules and classify equivalence classes.

This script:
1. Reads submodule paths from .gitmodules.
2. Optionally fetches each submodule history.
3. Collects all commit IDs from each submodule (git rev-list --all).
4. Builds commit-to-submodule mappings.
5. Computes equivalence classes where submodules are connected by at least one shared commit.
6. Writes analysis outputs to files.

Recommended execution with uv:
    uv run python scripts/analyze_submodule_commit_equivalence.py
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Set, Tuple


def run_git(args: Sequence[str], cwd: Path) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"git {' '.join(args)} failed in {cwd}:\n"
            f"{result.stderr.strip() or result.stdout.strip()}"
        )
    return result.stdout


def read_submodule_paths(repo_root: Path) -> List[str]:
    output = run_git(
        ["config", "-f", ".gitmodules", "--get-regexp", r"^submodule\..*\.path$"],
        cwd=repo_root,
    )
    paths: List[str] = []
    for line in output.splitlines():
        parts = line.strip().split(maxsplit=1)
        if len(parts) != 2:
            continue
        paths.append(parts[1].strip())
    return paths


def collect_commits_for_submodule(
    repo_root: Path, submodule_path: str, do_fetch: bool
) -> Set[str]:
    sub_path = repo_root / submodule_path
    if not sub_path.exists():
        raise RuntimeError(f"submodule path not found: {submodule_path}")

    if do_fetch:
        run_git(["fetch", "--all", "--tags", "--prune"], cwd=sub_path)

    rev_list = run_git(["rev-list", "--all"], cwd=sub_path)
    commits = {line.strip() for line in rev_list.splitlines() if line.strip()}
    return commits


class UnionFind:
    def __init__(self, items: Iterable[str]) -> None:
        self.parent: Dict[str, str] = {item: item for item in items}
        self.rank: Dict[str, int] = {item: 0 for item in items}

    def find(self, x: str) -> str:
        parent = self.parent[x]
        if parent != x:
            self.parent[x] = self.find(parent)
        return self.parent[x]

    def union(self, a: str, b: str) -> None:
        ra = self.find(a)
        rb = self.find(b)
        if ra == rb:
            return
        if self.rank[ra] < self.rank[rb]:
            self.parent[ra] = rb
        elif self.rank[ra] > self.rank[rb]:
            self.parent[rb] = ra
        else:
            self.parent[rb] = ra
            self.rank[ra] += 1


def write_tsv(path: Path, rows: Iterable[Tuple[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as f:
        f.write("commit_sha\tsubmodule\n")
        for sha, submodule in rows:
            f.write(f"{sha}\t{submodule}\n")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Classify submodules into equivalence classes by shared commits."
    )
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Repository root path where .gitmodules exists (default: current directory).",
    )
    parser.add_argument(
        "--output-dir",
        default="analysis/submodule-equivalence",
        help="Directory to write output files.",
    )
    parser.add_argument(
        "--fetch",
        action="store_true",
        help="Fetch each submodule before collecting commit IDs.",
    )
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        submodules = read_submodule_paths(repo_root)
    except Exception as exc:
        print(f"Error reading .gitmodules: {exc}", file=sys.stderr)
        return 1

    if not submodules:
        print("No submodules found in .gitmodules", file=sys.stderr)
        return 1

    submodule_to_commits: Dict[str, Set[str]] = {}
    for submodule in submodules:
        try:
            commits = collect_commits_for_submodule(repo_root, submodule, args.fetch)
        except Exception as exc:
            print(f"Error collecting commits for {submodule}: {exc}", file=sys.stderr)
            return 1
        submodule_to_commits[submodule] = commits

    commit_to_submodules: Dict[str, List[str]] = defaultdict(list)
    for submodule, commits in submodule_to_commits.items():
        for sha in commits:
            commit_to_submodules[sha].append(submodule)

    for sha in list(commit_to_submodules.keys()):
        commit_to_submodules[sha].sort()

    all_pairs: List[Tuple[str, str]] = []
    shared_pairs: List[Tuple[str, str]] = []
    for sha in sorted(commit_to_submodules.keys()):
        subs = commit_to_submodules[sha]
        for sub in subs:
            all_pairs.append((sha, sub))
            if len(subs) > 1:
                shared_pairs.append((sha, sub))

    uf = UnionFind(submodules)
    for subs in commit_to_submodules.values():
        if len(subs) < 2:
            continue
        first = subs[0]
        for other in subs[1:]:
            uf.union(first, other)

    classes: Dict[str, List[str]] = defaultdict(list)
    for submodule in submodules:
        classes[uf.find(submodule)].append(submodule)

    class_list: List[List[str]] = []
    for members in classes.values():
        members.sort()
        class_list.append(members)
    class_list.sort(key=lambda m: (-len(m), m))

    shared_commit_count = sum(1 for subs in commit_to_submodules.values() if len(subs) > 1)

    summary = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(repo_root),
        "submodule_count": len(submodules),
        "total_unique_commit_count": len(commit_to_submodules),
        "shared_commit_count": shared_commit_count,
        "equivalence_class_count": len(class_list),
        "equivalence_classes": class_list,
        "submodule_commit_counts": {
            sub: len(submodule_to_commits[sub]) for sub in sorted(submodule_to_commits.keys())
        },
        "output_files": {
            "all_pairs_tsv": "commit_to_submodule.tsv",
            "shared_pairs_tsv": "shared_commit_to_submodule.tsv",
            "summary_json": "equivalence_classes.json",
        },
    }

    write_tsv(output_dir / "commit_to_submodule.tsv", all_pairs)
    write_tsv(output_dir / "shared_commit_to_submodule.tsv", shared_pairs)
    (output_dir / "equivalence_classes.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"Analyzed {len(submodules)} submodules.")
    print(f"Unique commits: {len(commit_to_submodules)}")
    print(f"Shared commits: {shared_commit_count}")
    print(f"Equivalence classes: {len(class_list)}")
    print(f"Output: {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
