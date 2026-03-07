# Git Related Branch Detector

**Author:** Takashi Sasaki ([@TakashiSasaki](https://x.com/TakashiSasaki))

This tool helps visualize the relationship between the current branch and other branches, including remote tracking branches and reflog entries.

## Quick Run

You can run this application directly from GitHub using `uvx`:

```bash
uvx --refresh --from git+https://github.com/TakashiSasaki/public.git@git-local-repo-viewer gui
```

## Features

- Visualize relationships (Ancestor, Tip, Diverged, Independent).
- Support for Reflog entries and Remote tracking branches.
- Rich GUI with filters and real-time status.
