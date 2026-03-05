---
name: remaining_branches_submodule_adder
description: Automatically add missing remote branches as submodules in the root directory.
---

# Remaining Branches Submodule Adder

This skill scans the remote `origin` repository for branches that are not yet configured as submodules in the current repository and adds them automatically.

## Usage

```powershell
pwsh .agent/skills/remaining_branches_submodule_adder/scripts/add_remaining_branches_as_submodules.ps1
```

## Options

- `-DryRun`: Show which branches would be added without actually performing the `git submodule add` command.

## Behavior

1. Fetches the latest branch list from `origin`.
2. Compares with currently configured submodules.
3. Adds any missing branches (excluding `master` and `public.moukaeritai.work`).
4. Uses the branch name as the submodule path.
