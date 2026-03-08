# PyPI Publishing Guide (Security Best Practices)

This document outlines how to securely manage PyPI API tokens when publishing packages using `uv`.

## 1. Using OS-level Credential Stores (Recommended)

`uv` can integrate with your operating system's native secure storage (e.g., Windows Credential Manager, macOS Keychain) to store your credentials securely.

### Login
Run the following command to store your token:

```powershell
uv auth login https://upload.pypi.org/legacy/
```

- **Username**: `__token__`
- **Password**: Your PyPI API token (`pypi-...`)

Once stored, you can run `uv publish` without ever typing your password again.

---

## 2. Using Environment Variables (.env)

If you need to automate publishing or prefer not to use the system-wide store, you can use environment variables.

> [!WARNING]
> Never commit your `.env` file to version control. Ensure `.env` is listed in your `.gitignore`.

### Setup
Create a `.env` file in your repository root:

```text
UV_PUBLISH_TOKEN=pypi-your-token-string
```

### Usage (PowerShell)
To load the token from `.env` and publish:

```powershell
# Load .env into the current process session
item -Path .env | Get-Content | ForEach-Object { $name, $value = $_.Split('=', 2); [System.Environment]::SetEnvironmentVariable($name, $value, "Process") }

# Publish without password prompt
uv publish
```

---

## 3. Security Checkpoints

- **Token Scoping**: Use "Project-scoped" tokens whenever possible instead of "Account-scoped" tokens to minimize the impact of a potential leak.
- **Git Safety**: Always verify that `.env` or any file containing secrets is explicitly ignored in `.gitignore`.
- **Credential Cleanup**: If you suspect a token is compromised, revoke it immediately from the [PyPI Account Settings](https://pypi.org/manage/account/token/).
