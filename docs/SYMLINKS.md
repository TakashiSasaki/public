# Technical Note: Cross-Platform Symbolic Link Handling

This document details the technical challenges and solutions regarding symbolic links in a cross-platform (Windows/WSL/Linux) environment, specifically within the `get-a-grip` project.

## 1. The Problem Statement

When a symbolic link is created using `ln -s` within **Git Bash** or **WSL** on a Windows host, it may appear as a **0-byte file** in native Windows environments (PowerShell, CMD, or Explorer). Furthermore, native Windows Git (`git.exe`) may fail to `git add` or even read such files, reporting an `Invalid argument` or `Permission denied` error.

## 2. Theoretical Background: The "Three Species" of Symlinks

Windows NTFS supports several types of "reparse points," leading to different, often incompatible, symbolic link behaviors:

### A. Windows Native Symlinks (NT Symlinks)
*   **Created by:** `mklink` (CMD) or `New-Item -ItemType SymbolicLink` (PowerShell).
*   **Reparse Tag:** `IO_REPARSE_TAG_SYMLINK` (`0xA000000C`).
*   **Behavior:** Fully recognized by all Windows APIs and WSL. 
*   **Limitation:** Requires "Developer Mode" or Administrative privileges on Windows.

### B. WSL Symlinks (Reparse Point Type)
*   **Created by:** `ln -s` inside WSL, and critically, **`ln -s` inside Git for Windows' Bash** (depending on the `MSYS` environment variable configuration).
*   **Reparse Tag:** `IO_REPARSE_TAG_LX_SYMLINK` (`0xA000001D`).
*   **Behavior:** Works correctly inside WSL and Git Bash sessions. However, to native Win32 APIs (PowerShell, CMD, Explorer, VS Code, Python), it appears as a **0-byte file with an unknown reparse tag**. Native Windows Git (`git.exe`) cannot open these files and will fail to commit them.

### C. Git Bash / MSYS2 Emulated Symlinks
*   **Created by:** `ln -s` in Git Bash when `MSYS=winsymlinks` is not set.
*   **Behavior:** Often implemented as a system file with a `.lnk` extension or a specific bit set. Only recognized within the MSYS2/Bash emulation layer.

## 3. Identification and Diagnosis

If you encounter a suspicious file that behaves like a link in Bash but is broken in Windows, use `fsutil` to inspect the reparse point:

```powershell
# Query reparse point information
fsutil reparsepoint query path/to/file
```

If the **Reparse Tag Value** is `0xa000001d`, it is a WSL-style symlink that native Windows tools cannot resolve.

## 4. The Solution: Git-Native Symbolic Links

To ensure a link works on Linux/WSL while remaining manageable on Windows without specific NTFS driver support, we use **Git Index Injection**.

Git tracks symbolic links using a specific file mode: **`120000`**. By manually pathing the Git index, we can define a file as a symlink regardless of how the local OS handles reparse points.

### Recovery/Manual Creation Steps (Windows)

If you need to create or fix a symlink (e.g., `schema/filelist.schema.json` pointing to `output-filelist.schema.json`):

1.  **Generate the Blob Hash:**
    ```powershell
    # Create a blob of the target path string (no newlines)
    $hash = python -c "import subprocess; p=subprocess.Popen(['git', 'hash-object', '-w', '--stdin'], stdin=subprocess.PIPE, stdout=subprocess.PIPE); print(p.communicate(input=b'output-filelist.schema.json')[0].decode().strip())"
    ```

2.  **Update the Git Index:**
    ```powershell
    # Manually add the entry with mode 120000
    git update-index --add --cacheinfo 120000,$hash,schema/filelist.schema.json
    ```

3.  **Checkout to Materialize:**
    ```powershell
    git checkout schema/filelist.schema.json
    ```

## 5. Summary for Developers

*   **Do not use `ln -s` in Git Bash** unless you have configured it to create native Windows symlinks.
*   **Git-Native Symlinks** (Mode 120000) are the preferred format for this repository.
*   On Windows, these will appear as **text files** containing the target path string.
*   On Linux/WSL, Git will automatically materialize these as **functional symbolic links** during clone or checkout.

---
*Created on: 2026-02-06*
