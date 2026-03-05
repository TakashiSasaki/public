---
name: submodule_equivalence_analyzer
description: Analyze shared commit history across git submodules and classify equivalence classes.
---

# Submodule Equivalence Analyzer

This skill analyzes shared commit history across all configured git submodules to identify branch/submodule equivalence.

## Usage

```bash
uv run python .agent/skills/submodule_equivalence_analyzer/scripts/analyze_submodule_commit_equivalence.py --fetch
```

## Options

- `--repo-root`: Path to the repository root (default: current directory).
- `--output-dir`: Directory to write analysis results (default: `analysis/submodule-equivalence`).
- `--fetch`: Fetch each submodule's history before analysis.
- `--help`: Show help message.

## Output

The skill generates:
- `commit_to_submodule.tsv`: Mapping of every commit to its containing submodules.
- `shared_commit_to_submodule.tsv`: Mapping of shared commits only.
- `equivalence_classes.json`: Grouping of submodules that share history.
