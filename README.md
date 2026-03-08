# Git Related Branch Detector

**Author:** Takashi Sasaki ([@TakashiSasaki](https://x.com/TakashiSasaki))

This tool helps visualize the relationship between the current branch and other branches, including remote tracking branches and reflog entries.

## Project Philosophy: The Viewer's Promise
This application is designed as a **read-only viewer**. Its core mission is to provide clarity and insight into Git repositories without ever altering them. 

- **No Modifications**: The GUI does not and will not provide features to commit, branch, merge, or otherwise modify the repository state.
- **Safe Exploration**: Users can explore complex branch relationships and submodule states with total confidence that their repository remains untouched.
- **Separated Concerns**: State-changing operations are left to the Git CLI or primary clients, ensuring this tool remains a safe, passive observer.

## Quick Run

You can run this application directly from GitHub using `uvx`:

```bash
uvx --refresh --from git+https://github.com/TakashiSasaki/public.git@git-local-repo-viewer gui
```

## Features

- Visualize relationships (Ancestor, Tip, Diverged, Independent).
- Support for Reflog entries and Remote tracking branches.
- Rich GUI with filters and real-time status.
