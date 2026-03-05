<#
.SYNOPSIS
Synchronizes remote branches from the 'origin' repository into local submodules.

.DESCRIPTION
This script fetches the latest remote branches from 'origin'. It then identifies
branches that are not currently checked out as submodules directly under the root
directory. For any missing branches (excluding specific ones like 'public.moukaeritai.work'
and 'master'), it adds them as a submodule. Temporary files are stored in the '.tmp' directory.
#>

param (
    [switch]$DryRun
)

# Define directories and branches to ignore
$TmpDir = ".tmp"
$IgnoredBranches = @("public.moukaeritai.work", "master")

# Ensure .tmp directory exists
if (-not (Test-Path -Path $TmpDir)) {
    Write-Output "Creating $TmpDir directory..."
    if (-not $DryRun) {
        New-Item -ItemType Directory -Force -Path $TmpDir | Out-Null
    }
}

Write-Output "Fetching latest changes from public..."
if (-not $DryRun) {
    git fetch public
}

# 1. Get the list of all remote branches
$RemoteBranchesFile = Join-Path -Path $TmpDir -ChildPath "remote_branches.txt"
Write-Output "Retrieving remote branch list..."

if (-not $DryRun) {
    # Extract just the branch names (e.g., refs/heads/branch_name -> branch_name)
    git ls-remote --heads public | ForEach-Object {
        if ($_ -match "refs/heads/(.*)") {
            $matches[1]
        }
    } | Out-File -FilePath $RemoteBranchesFile -Encoding UTF8
}

if (-not (Test-Path -Path $RemoteBranchesFile) -and -not $DryRun) {
    Write-Error "Failed to retrieve remote branches."
    exit 1
}

# 2. Identify currently configured submodules
$CurrentSubmodulesFile = Join-Path -Path $TmpDir -ChildPath "current_submodules.txt"
Write-Output "Retrieving current submodule list..."

if (-not $DryRun) {
    # Extract just the path names from git submodule status
    # Output format is typically: " <commit_hash> <path> (<describe>)"
    git submodule status | ForEach-Object {
        $parts = $_.Trim() -split "\s+"
        if ($parts.Count -ge 2) {
            $parts[1]
        }
    } | Out-File -FilePath $CurrentSubmodulesFile -Encoding UTF8
}

# Read the lists
$RemoteBranches = @()
if (Test-Path -Path $RemoteBranchesFile) {
    $RemoteBranches = Get-Content -Path $RemoteBranchesFile
}

$CurrentSubmodules = @()
if (Test-Path -Path $CurrentSubmodulesFile) {
    $CurrentSubmodules = Get-Content -Path $CurrentSubmodulesFile
}

# 3. Add missing branches as submodules
$AddedCount = 0

foreach ($Branch in $RemoteBranches) {
    # Skip ignored branches
    if ($IgnoredBranches -contains $Branch) {
        continue
    }

    # Check if the branch is already a submodule
    if ($CurrentSubmodules -contains $Branch) {
        continue
    }

    Write-Output "Adding missing branch '$Branch' as submodule..."
    
    if (-not $DryRun) {
        $OriginUrl = (git remote get-url public).Trim()
        
        # Add the submodule. The path will be the branch name.
        $Command = "git submodule add -b `"$Branch`" `"$OriginUrl`" `"$Branch`""
        Invoke-Expression $Command
        
        if ($LASTEXITCODE -eq 0) {
            Write-Output "Successfully added '$Branch'"
            $AddedCount++
        }
        else {
            Write-Warning "Failed to add '$Branch'"
        }
    }
    else {
        Write-Output "[DryRun] Would add '$Branch' from remote origin."
        $AddedCount++
    }
}

if ($AddedCount -eq 0) {
    Write-Output "All remote branches are already configured as submodules."
}
else {
    Write-Output "Finished adding $AddedCount submodules."
}

Write-Output "Sync process complete."
