# Windows Python Environment Guide for Linux Developers

This guide provides hints for developers familiar with Linux who are new to developing Python applications on Windows. It specifically focuses on identifying the execution environment and understanding how tools like Poetry interact with the Windows shell (PowerShell).

## Finding the Python Interpreter

In Linux, you typically use `which python` to see which executable is being used. On Windows (PowerShell), the equivalent command is `Get-Command` (or its alias `gcm`).

```powershell
# Check the current python executable path
Get-Command python

# Check all available python executables in PATH (like `which -a python`)
Get-Command python -All
```

### Common Output Patterns

**1. System Python:**
If you see a path like `C:\Program Files\Python312\python.exe`, you are using the global system Python.

**2. Windows Store Python:**
If you see `C:\Users\<User>\AppData\Local\Microsoft\WindowsApps\python.exe`, this is a "execution stub" provided by Windows. It may launch the Microsoft Store to install Python if it's not actually installed, or forward to a real installation. This can sometimes be a source of confusion.

**3. Virtual Environment (Poetry):**
If you see a path deep inside `AppData` like `C:\Users\<User>\AppData\Local\pypoetry\Cache\virtualenvs\...`, you are successfully running inside a Poetry virtual environment.

## Poetry and Virtual Environments on Windows

Poetry works similarly on Windows as it does on Linux, but the location of environments differs.

### Checking the Current Environment

To see where Poetry has created the virtual environment for the current project:

```powershell
poetry env info
```

This will display the **Path** to the virtual environment (e.g., `C:\Users\takas\AppData\Local\pypoetry\Cache\virtualenvs\get-a-grip-xxxxx-py3.12`).

### Running Commands

Just like on Linux, `poetry run` executes commands within the virtual environment context, even if your current shell is using the system Python.

```powershell
# Runs using the virtual environment's python
poetry run python --version

# Runs using the system python (if not activated)
python --version
```

### Activating the Shell

To activate the virtual environment in your current PowerShell session (similar to `source .venv/bin/activate`):

```powershell
poetry shell
```

Once activated, `Get-Command python` should point to the executable inside the `virtualenvs` directory mentioned above.

## Environment Variables

To view environment variables in PowerShell, use the `env:` drive:

```powershell
# View PYTHONPATH
$env:PYTHONPATH

# View simple list of all env vars (like printenv)
Get-ChildItem env:
```

## Shebangs (`#!`)

Windows generally ignores the Shebang line (`#!/usr/bin/env python3`) at the top of scripts unless you use the `py` launcher. When running scripts via `poetry run python script.py` or `python script.py`, the interpreter is determined by the command you use, not the file header.
