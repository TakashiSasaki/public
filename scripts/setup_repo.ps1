# Consolidated Repository Setup Script
# Usage: powershell -ExecutionPolicy Bypass -File .\scripts\setup_repo.ps1

Write-Host "--- Git Repository Setup Initializing ---" -ForegroundColor Cyan

# 1. Configure Git Remote Fetch
$remote = "public"
$branch = "llama-cpp-tk"
# Use format operator to avoid interpolation/scope issues
$fetch_ref = "+refs/heads/{0}:refs/remotes/{1}/{0}" -f $branch, $remote

Write-Host "[1/2] Configuring remote '$remote' fetch behavior..."
Write-Host "Desired refspec: $fetch_ref"

$remotes = git remote
if ($null -eq $remotes) { $remotes = @() }
Write-Host "Detected remotes: $($remotes -join ', ')"

if ($remotes -contains $remote -or (git remote | Select-String -Pattern "^$remote$")) {
    git config "remote.$remote.fetch" "$fetch_ref"
    Write-Host " Done." -ForegroundColor Green
} else {
    Write-Host " Skipped (Remote '$remote' not found)." -ForegroundColor Yellow
}

# 2. Setup Git Hooks
Write-Host "[2/2] Setting up Git hooks..." -NoNewline
$hooks_dir = ".git/hooks"
$hook_src = "scripts/git-hooks/pre-commit.sh"
$hook_dst = "$hooks_dir/pre-commit"

if (Test-Path $hook_src) {
    if (-not (Test-Path $hooks_dir)) {
        New-Item -ItemType Directory -Path $hooks_dir -Force | Out-Null
    }
    Copy-Item -Path $hook_src -Destination $hook_dst -Force
    Write-Host " Done (pre-commit hook installed)." -ForegroundColor Green
} else {
    Write-Host " Failed (Source hook template not found at $hook_src)." -ForegroundColor Red
}

Write-Host "--- Setup Complete ---" -ForegroundColor Cyan
