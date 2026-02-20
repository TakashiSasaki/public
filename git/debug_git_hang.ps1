$gitDir = "H:\.git"

Write-Host "=== Git Environment Debugging ==="

# 1. Locate .git
if (!(Test-Path $gitDir)) {
    Write-Host ".git not found at H:\. Checking parent directories..."
    # Simple check up one level for H:\server-certification if it was a repo
    if (Test-Path "H:\server-certification\.git") {
        $gitDir = "H:\server-certification\.git"
    } else {
        Write-Host "Could not find .git at H root. Assuming it exists somewhere above or within H."
        # If not found, we can't inspect it directly, but we can try running git on H:
    }
}

if (Test-Path $gitDir) {
    Write-Host "Found .git at: $gitDir"

    # 2. Inspect Config
    $configFile = Join-Path $gitDir "config"
    if (Test-Path $configFile) {
        Write-Host "Reading config..."
        Get-Content $configFile | Select-String "filemode"
        Get-Content $configFile | Select-String "fscache"
    }

    # 3. Check for Lock Files
    if (Test-Path (Join-Path $gitDir "index.lock")) {
        Write-Host "WARNING: index.lock exists! This might be the cause."
    }
    
    # 4. Check Permissions of .git folder
    try {
        $acl = Get-Acl $gitDir
        Write-Host ".git Owner: $($acl.Owner)"
    } catch {
        Write-Host "Failed to get ACL of .git: $_"
    }
}

# 5. Run Git Status with Trace
Write-Host "`n=== Attempting Git Status (with Timeout) ==="
$env:GIT_TRACE = "1"
$env:GIT_TRACE_PACKET = "1" # Should be empty for local repo, but useful if weird setup
$env:GIT_TRACE_PERFORMANCE = "1"

$targetDir = "H:\server-certification\yoran\20260115"
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$logFile = "$PSScriptRoot\git_trace_$timestamp.log"
$logPathForGit = $logFile.Replace("\", "/")

# Check write access to .git
if (Test-Path $gitDir) {
    Try {
        $testFile = Join-Path $gitDir "test_write_$timestamp.tmp"
        New-Item $testFile -ItemType File -Value "test" -Force | Out-Null
        Write-Host "Write access to .git: OK"
        Remove-Item $testFile -Force
    } Catch {
        Write-Host "Write access to .git: FAILED ($extension)"
    }
}

Write-Host "Running git status in $targetDir with trace logging to $logPathForGit..."

$job = Start-Job -ScriptBlock {
    param($dir, $log)
    $env:GIT_TRACE = $log
    $env:GIT_TRACE_PERFORMANCE = $log
    $env:GIT_TRACE_PACKET = $log
    git -C $dir status
} -ArgumentList $targetDir, $logPathForGit

if (Wait-Job $job -Timeout 10) {
    Receive-Job $job
} else {
    Write-Host "Git status timed out after 10 seconds."
    Stop-Job $job
    Remove-Job $job
}

if (Test-Path $logFile) {
    Write-Host "`n=== Trace Log Output ==="
    Get-Content $logFile
} else {
    Write-Host "No log file generated."
}
